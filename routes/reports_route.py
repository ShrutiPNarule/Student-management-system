# routes/reports_route.py

from flask import render_template, session, redirect, url_for, flash, abort, request, send_file
from app import app
from db import get_connection
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from datetime import datetime
import io


@app.route("/reports")
def reports():
    """Display reports filter page - Admin and Superadmin only"""
    if "user_email" not in session:
        session["next_url"] = url_for("reports")
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    role = session.get("role")
    
    # Only admin and superadmin can access reports
    if role not in ("admin", "superadmin"):
        flash("You don't have permission to access reports.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    # Get filter options from database
    # Schools
    cur.execute("SELECT id, name FROM schools_master ORDER BY name;")
    schools = cur.fetchall()

    # Colleges
    cur.execute("SELECT id, name FROM colleges_master ORDER BY name;")
    colleges = cur.fetchall()

    # Get distinct states from schools
    cur.execute("SELECT DISTINCT state FROM schools_master WHERE state IS NOT NULL ORDER BY state;")
    states_school = [row[0] for row in cur.fetchall()]

    # Get distinct states from colleges
    cur.execute("SELECT DISTINCT state FROM colleges_master WHERE state IS NOT NULL ORDER BY state;")
    states_college = [row[0] for row in cur.fetchall()]

    states = list(set(states_school + states_college))
    states.sort()

    # Get distinct board types
    cur.execute("SELECT DISTINCT board FROM schools_master WHERE board IS NOT NULL ORDER BY board;")
    boards = [row[0] for row in cur.fetchall()]

    # Get distinct college types
    cur.execute("SELECT DISTINCT institute_type FROM colleges_master WHERE institute_type IS NOT NULL ORDER BY institute_type;")
    college_types = [row[0] for row in cur.fetchall()]

    cur.close()

    return render_template(
        "reports.html",
        schools=schools,
        colleges=colleges,
        states=states,
        boards=boards,
        college_types=college_types
    )


@app.route("/generate-report", methods=["POST"])
def generate_report():
    """Generate filtered report and return as PDF"""
    # Authentication check
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ("admin", "superadmin"):
        abort(403)

    # Extract filters
    filters = _extract_filters()
    
    # Fetch filtered student data
    students = _fetch_filtered_students(filters)
    
    # Generate and return PDF
    pdf_buffer = _generate_pdf(students, filters)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"student_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )


def _extract_filters():
    """Extract filter parameters from form request"""
    return {
        "marks_10th_min": request.form.get("marks_10th_min", ""),
        "marks_10th_max": request.form.get("marks_10th_max", ""),
        "marks_12th_min": request.form.get("marks_12th_min", ""),
        "marks_12th_max": request.form.get("marks_12th_max", ""),
        "school_id": request.form.get("school_id", ""),
        "college_id": request.form.get("college_id", ""),
        "state": request.form.get("state", ""),
        "board": request.form.get("board", ""),
        "college_type": request.form.get("college_type", ""),
        "current_status": request.form.get("current_status", ""),
    }


def _fetch_filtered_students(filters):
    """Fetch students based on applied filters"""
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            s.id, u.name, s.enrollment_no, u.email, u.phone, u.address,
            m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4,
            sc.name as school_name, sc.board, sc.state as school_state,
            cl.name as college_name, cl.institute_type, cl.state as college_state,
            s.current_status
        FROM students_master s
        LEFT JOIN users_master u ON s.user_id = u.id
        LEFT JOIN student_marks m ON s.id = m.student_id
        LEFT JOIN student_school_history ssh ON s.id = ssh.student_id
        LEFT JOIN schools_master sc ON ssh.school_id = sc.id
        LEFT JOIN college_enrollment ce ON s.id = ce.student_id
        LEFT JOIN colleges_master cl ON ce.college_id = cl.id
        WHERE s.is_deleted = FALSE AND m.is_deleted = FALSE
    """
    
    params = []
    
    # Apply numeric filters
    _add_numeric_filter(query, params, filters, "marks_10th_min", "m.marks_10th", ">=")
    _add_numeric_filter(query, params, filters, "marks_10th_max", "m.marks_10th", "<=")
    _add_numeric_filter(query, params, filters, "marks_12th_min", "m.marks_12th", ">=")
    _add_numeric_filter(query, params, filters, "marks_12th_max", "m.marks_12th", "<=")
    
    # Apply string filters
    if filters["school_id"]:
        query += " AND ssh.school_id = %s"
        params.append(filters["school_id"])
    
    if filters["college_id"]:
        query += " AND ce.college_id = %s"
        params.append(filters["college_id"])
    
    if filters["state"]:
        query += " AND (sc.state = %s OR cl.state = %s)"
        params.extend([filters["state"], filters["state"]])
    
    if filters["board"]:
        query += " AND sc.board = %s"
        params.append(filters["board"])
    
    if filters["college_type"]:
        query += " AND cl.institute_type = %s"
        params.append(filters["college_type"])
    
    if filters["current_status"]:
        query += " AND s.current_status = %s"
        params.append(filters["current_status"])

    query += " ORDER BY u.name;"
    
    cur.execute(query, params)
    students = cur.fetchall()
    cur.close()
    
    return students


def _add_numeric_filter(query, params, filters, filter_key, field_name, operator):
    """Helper to add numeric filter to query"""
    if filters[filter_key]:
        try:
            value = int(filters[filter_key])
            query += f" AND {field_name} {operator} %s"
            params.append(value)
        except (ValueError, TypeError):
            pass


def _generate_pdf(students, filters):
    """Generate PDF document with report"""
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Add title
    _add_title(elements, styles)
    
    # Add report info
    _add_report_info(elements, styles, filters)
    
    # Add table
    _add_data_table(elements, styles, students)
    
    # Add footer
    _add_footer(elements, styles, len(students))
    
    doc.build(elements)
    pdf_buffer.seek(0)
    
    return pdf_buffer


def _add_title(elements, styles):
    """Add report title"""
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a3a52'),
        spaceAfter=10,
        alignment=1
    )
    elements.append(Paragraph("Student Report", title_style))


def _add_report_info(elements, styles, filters):
    """Add report generation date and applied filters"""
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=5
    )
    
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filter_text = f"<b>Report Generated:</b> {report_date}"
    
    if any(filters.values()):
        filter_text += "<br/><b>Filters Applied:</b> "
        filter_descriptions = _build_filter_descriptions(filters)
        filter_text += ", ".join(filter_descriptions)
    
    elements.append(Paragraph(filter_text, info_style))
    elements.append(Spacer(1, 0.3*inch))


def _build_filter_descriptions(filters):
    """Build human-readable filter descriptions"""
    descriptions = []
    filter_labels = {
        "marks_10th_min": "10th Marks Min",
        "marks_10th_max": "10th Marks Max",
        "marks_12th_min": "12th Marks Min",
        "marks_12th_max": "12th Marks Max",
        "school_id": "School",
        "college_id": "College",
        "state": "State",
        "board": "Board",
        "college_type": "College Type",
        "current_status": "Status",
    }
    
    for key, label in filter_labels.items():
        if filters[key]:
            descriptions.append(f"{label}: {filters[key]}")
    
    return descriptions


def _add_data_table(elements, styles, students):
    """Add student data table to report"""
    table_data = [["Name", "Email", "Phone", "10th Marks", "12th Marks", "School", "College", "Status"]]
    
    for student in students:
        table_data.append([
            str(student[1] or "N/A")[:20],
            str(student[3] or "N/A")[:20],
            str(student[4] or "N/A")[:12],
            str(student[6] or "N/A"),
            str(student[7] or "N/A"),
            str(student[12] or "N/A")[:15],
            str(student[15] or "N/A")[:15],
            str(student[18] or "N/A")
        ])

    if len(table_data) > 1:
        _add_styled_table(elements, table_data)
    else:
        _add_no_data_message(elements, styles)


def _add_styled_table(elements, table_data):
    """Create and style data table"""
    table = Table(
        table_data,
        colWidths=[1.0*inch, 1.1*inch, 0.9*inch, 0.8*inch, 0.8*inch, 1.0*inch, 1.0*inch, 0.8*inch]
    )
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a52')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)


def _add_no_data_message(elements, styles):
    """Add message when no data found"""
    no_data_style = ParagraphStyle(
        'NoData',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.red,
        alignment=1
    )
    elements.append(Paragraph("No students found matching the selected filters.", no_data_style))


def _add_footer(elements, styles, record_count):
    """Add report footer with record count"""
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=5
    )
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<i>Total Records: {record_count}</i>", info_style))

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
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    role = session.get("role")
    
    # Only admin and superadmin can access reports
    if role not in ("admin", "superadmin"):
        abort(403)

    # Get filter parameters from form
    filters = {
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

    # Build dynamic SQL query based on filters
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            s.id,
            u.name,
            s.enrollment_no,
            u.email,
            u.phone,
            u.address,
            m.marks_10th,
            m.marks_12th,
            m.marks1,
            m.marks2,
            m.marks3,
            m.marks4,
            sc.name as school_name,
            sc.board,
            sc.state as school_state,
            cl.name as college_name,
            cl.institute_type,
            cl.state as college_state,
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

    # Apply filters
    if filters["marks_10th_min"]:
        try:
            min_val = int(filters["marks_10th_min"])
            query += " AND m.marks_10th >= %s"
            params.append(min_val)
        except:
            pass

    if filters["marks_10th_max"]:
        try:
            max_val = int(filters["marks_10th_max"])
            query += " AND m.marks_10th <= %s"
            params.append(max_val)
        except:
            pass

    if filters["marks_12th_min"]:
        try:
            min_val = int(filters["marks_12th_min"])
            query += " AND m.marks_12th >= %s"
            params.append(min_val)
        except:
            pass

    if filters["marks_12th_max"]:
        try:
            max_val = int(filters["marks_12th_max"])
            query += " AND m.marks_12th <= %s"
            params.append(max_val)
        except:
            pass

    if filters["school_id"]:
        query += " AND ssh.school_id = %s"
        params.append(filters["school_id"])

    if filters["college_id"]:
        query += " AND ce.college_id = %s"
        params.append(filters["college_id"])

    if filters["state"]:
        query += " AND (sc.state = %s OR cl.state = %s)"
        params.append(filters["state"])
        params.append(filters["state"])

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

    # Generate PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a3a52'),
        spaceAfter=10,
        alignment=1  # Center alignment
    )
    
    title = Paragraph("Student Report", title_style)
    elements.append(title)
    
    # Report generated date and filters applied
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=5
    )
    
    filter_text = f"<b>Report Generated:</b> {report_date}"
    if any(filters.values()):
        filter_text += "<br/><b>Filters Applied:</b> "
        filter_descriptions = []
        if filters["marks_10th_min"]:
            filter_descriptions.append(f"10th Marks Min: {filters['marks_10th_min']}")
        if filters["marks_10th_max"]:
            filter_descriptions.append(f"10th Marks Max: {filters['marks_10th_max']}")
        if filters["marks_12th_min"]:
            filter_descriptions.append(f"12th Marks Min: {filters['marks_12th_min']}")
        if filters["marks_12th_max"]:
            filter_descriptions.append(f"12th Marks Max: {filters['marks_12th_max']}")
        if filters["school_id"]:
            filter_descriptions.append(f"School: {filters['school_id']}")
        if filters["college_id"]:
            filter_descriptions.append(f"College: {filters['college_id']}")
        if filters["state"]:
            filter_descriptions.append(f"State: {filters['state']}")
        if filters["board"]:
            filter_descriptions.append(f"Board: {filters['board']}")
        if filters["college_type"]:
            filter_descriptions.append(f"College Type: {filters['college_type']}")
        if filters["current_status"]:
            filter_descriptions.append(f"Status: {filters['current_status']}")
        filter_text += ", ".join(filter_descriptions)
    
    elements.append(Paragraph(filter_text, info_style))
    elements.append(Spacer(1, 0.3*inch))

    # Table data
    table_data = [
        ["Name", "Email", "Phone", "10th Marks", "12th Marks", "School", "College", "Status"]
    ]

    for student in students:
        name = student[1] or "N/A"
        email = student[3] or "N/A"
        phone = student[4] or "N/A"
        marks_10th = student[6] or "N/A"
        marks_12th = student[7] or "N/A"
        school_name = student[12] or "N/A"
        college_name = student[15] or "N/A"
        status = student[18] or "N/A"

        table_data.append([
            str(name)[:20],
            str(email)[:20],
            str(phone)[:12],
            str(marks_10th),
            str(marks_12th),
            str(school_name)[:15],
            str(college_name)[:15],
            str(status)
        ])

    # Create table with styling
    if len(table_data) > 1:
        table = Table(table_data, colWidths=[1.0*inch, 1.1*inch, 0.9*inch, 0.8*inch, 0.8*inch, 1.0*inch, 1.0*inch, 0.8*inch])
        
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
    else:
        no_data_style = ParagraphStyle(
            'NoData',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.red,
            alignment=1
        )
        elements.append(Paragraph("No students found matching the selected filters.", no_data_style))

    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_text = f"<i>Total Records: {len(table_data) - 1}</i>"
    elements.append(Paragraph(footer_text, info_style))

    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"student_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

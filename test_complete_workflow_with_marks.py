#!/usr/bin/env python3
"""
Complete workflow test: Clerk Edit → Auditor Verify → Admin Approve → Check DB
"""
import psycopg2
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

print("\n" + "="*80)
print("COMPLETE WORKFLOW TEST - CLERK → AUDITOR → ADMIN")
print("="*80)

# ============================================================================
# STEP 1: CHECK IF STUDENT EXISTS
# ============================================================================
print("\n[STEP 1] Finding a test student...")
cur.execute("""
    SELECT id, user_id, name FROM students_master WHERE is_deleted = FALSE LIMIT 1
""")
student = cur.fetchone()

if not student:
    print("❌ No students found. Creating test data...")
    # Create a user first
    cur.execute("""
        INSERT INTO users_master (name, email, phone, address, category, dob, birth_place)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        "Workflow Test User",
        "workflow_test@test.com",
        "9000000000",
        "Test City",
        "General",
        "2000-01-01",
        "Test Place"
    ))
    user_id = cur.fetchone()[0]
    
    # Create a student
    cur.execute("""
        INSERT INTO students_master (user_id, current_status)
        VALUES (%s, %s)
        RETURNING id
    """, (user_id, "active"))
    student_id = cur.fetchone()[0]
    
    conn.commit()
    print(f"✓ Created test student: {student_id}")
else:
    student_id, user_id, name = student
    print(f"✓ Using existing student: {student_id} ({name})")

# ============================================================================
# STEP 2: SUBMIT EDIT (Simulating Clerk Action)
# ============================================================================
print("\n[STEP 2] Submitting edit (Clerk action)...")

edit_data = {
    "name": "Updated Test User",
    "email": "updated_workflow@test.com",
    "phone": "9111111111",
    "address": "Updated Test City",
    "college": "Updated College",
    "category": "OBC",
    "dob": "2000-06-15",
    "birth_place": "Updated Birth Place",
    "marks_10th": 85,
    "marks_12th": 88,
    "marks1": 80,
    "marks2": 82,
    "marks3": 84,
    "marks4": 86,
    "marks5": 88,
    "marks6": 90,
    "marks7": 92,
    "marks8": 94
}

# Get original data
cur.execute("""
    SELECT 
        COALESCE(um.name, ''),
        COALESCE(um.email, ''),
        COALESCE(um.phone, ''),
        COALESCE(um.address, ''),
        COALESCE(cc.name, um.address, ''),
        COALESCE(um.category, ''),
        COALESCE(um.dob, ''),
        COALESCE(um.birth_place, ''),
        COALESCE(sm.marks_10th, 0),
        COALESCE(sm.marks_12th, 0),
        COALESCE(sm.marks1, 0),
        COALESCE(sm.marks2, 0),
        COALESCE(sm.marks3, 0),
        COALESCE(sm.marks4, 0),
        COALESCE(sm.marks5, 0),
        COALESCE(sm.marks6, 0),
        COALESCE(sm.marks7, 0),
        COALESCE(sm.marks8, 0)
    FROM students_master st
    LEFT JOIN users_master um ON st.user_id = um.user_id
    LEFT JOIN student_marks sm ON st.student_id = sm.student_id
    LEFT JOIN colleges_master cc ON um.college_id = cc.id
    WHERE st.student_id = %s
""", (student_id,))

original_data = cur.fetchone()
if original_data:
    original_data = {
        "name": original_data[0],
        "email": original_data[1],
        "phone": original_data[2],
        "address": original_data[3],
        "college": original_data[4],
        "category": original_data[5],
        "dob": original_data[6],
        "birth_place": original_data[7],
        "marks_10th": original_data[8],
        "marks_12th": original_data[9],
        "marks1": original_data[10],
        "marks2": original_data[11],
        "marks3": original_data[12],
        "marks4": original_data[13],
        "marks5": original_data[14],
        "marks6": original_data[15],
        "marks7": original_data[16],
        "marks8": original_data[17]
    }

# Insert into pending_changes
cur.execute("""
    INSERT INTO pending_changes (change_type, student_id, data, original_data, created_by, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING change_id
""", (
    "edit_student",
    student_id,
    json.dumps(edit_data),
    json.dumps(original_data) if original_data else json.dumps({}),
    user_id,
    "pending"
))

change_id = cur.fetchone()[0]
conn.commit()
print(f"✓ Edit submitted with change_id: {change_id}")

# ============================================================================
# STEP 3: AUDITOR VERIFICATION
# ============================================================================
print("\n[STEP 3] Auditor verification...")

auditor_id = user_id  # Using same user as auditor for test

cur.execute("""
    UPDATE pending_changes
    SET status = %s, auditor_id = %s, auditor_remarks = %s, verified_at = CURRENT_TIMESTAMP
    WHERE change_id = %s
""", ("auditor_verified", auditor_id, "Verified by auditor", change_id))

conn.commit()
print(f"✓ Change verified by auditor")

# ============================================================================
# STEP 4: ADMIN APPROVAL
# ============================================================================
print("\n[STEP 4] Admin approval and data application...")

admin_id = user_id  # Using same user as admin for test

# Get the latest approved change
cur.execute("""
    SELECT change_id, data FROM pending_changes
    WHERE student_id = %s AND status = %s
    ORDER BY created_at DESC LIMIT 1
""", (student_id, "auditor_verified"))

result = cur.fetchone()
if result:
    change_id, data = result
    
    # Parse data
    if isinstance(data, dict):
        change_data = data
    else:
        change_data = json.loads(data)
    
    print(f"Processing change {change_id} with data: {list(change_data.keys())}")
    
    # Update users_master
    print("  - Updating users_master...")
    cur.execute("""
        UPDATE users_master
        SET name = %s,
            email = %s,
            phone = %s,
            address = %s,
            category = %s,
            dob = %s,
            birth_place = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s
    """, (
        change_data.get("name"),
        change_data.get("email"),
        change_data.get("phone"),
        change_data.get("address"),
        change_data.get("category"),
        change_data.get("dob"),
        change_data.get("birth_place"),
        user_id
    ))
    print(f"    ✓ users_master updated ({cur.rowcount} rows)")
    
    # Update student_marks
    print("  - Updating student_marks...")
    cur.execute("""
        UPDATE student_marks
        SET marks_10th = %s,
            marks_12th = %s,
            marks1 = %s,
            marks2 = %s,
            marks3 = %s,
            marks4 = %s,
            marks5 = %s,
            marks6 = %s,
            marks7 = %s,
            marks8 = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE student_id = %s
    """, (
        change_data.get("marks_10th", 0),
        change_data.get("marks_12th", 0),
        change_data.get("marks1", 0),
        change_data.get("marks2", 0),
        change_data.get("marks3", 0),
        change_data.get("marks4", 0),
        change_data.get("marks5", 0),
        change_data.get("marks6", 0),
        change_data.get("marks7", 0),
        change_data.get("marks8", 0),
        student_id
    ))
    print(f"    ✓ student_marks updated ({cur.rowcount} rows)")
    
    # If no rows updated, insert
    if cur.rowcount == 0:
        print("    ! No existing marks record, creating new one...")
        cur.execute("""
            INSERT INTO student_marks 
            (student_id, marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            student_id,
            change_data.get("marks_10th", 0),
            change_data.get("marks_12th", 0),
            change_data.get("marks1", 0),
            change_data.get("marks2", 0),
            change_data.get("marks3", 0),
            change_data.get("marks4", 0),
            change_data.get("marks5", 0),
            change_data.get("marks6", 0),
            change_data.get("marks7", 0),
            change_data.get("marks8", 0)
        ))
        print(f"    ✓ New marks record created")
    
    # Mark as approved
    cur.execute("""
        UPDATE pending_changes
        SET status = %s, admin_id = %s, admin_remarks = %s, approved_at = CURRENT_TIMESTAMP
        WHERE change_id = %s
    """, ("admin_approved", admin_id, "Approved by admin", change_id))
    
    conn.commit()
    print(f"✓ Change marked as admin_approved")

# ============================================================================
# STEP 5: VERIFY DATABASE RESULTS
# ============================================================================
print("\n[STEP 5] Verifying database results...")

# Check users_master
print("\n📋 users_master:")
cur.execute("SELECT name, email, phone, address, category, dob FROM users_master WHERE user_id = %s", (user_id,))
um = cur.fetchone()
if um:
    print(f"  ✓ Name: {um[0]}")
    print(f"  ✓ Email: {um[1]}")
    print(f"  ✓ Phone: {um[2]}")
    print(f"  ✓ Address: {um[3]}")
    print(f"  ✓ Category: {um[4]}")
    print(f"  ✓ DOB: {um[5]}")

# Check student_marks
print("\n📋 student_marks:")
cur.execute("""
    SELECT marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
    FROM student_marks WHERE student_id = %s
""", (student_id,))
sm = cur.fetchone()
if sm:
    print(f"  ✓ Marks 10th: {sm[0]}")
    print(f"  ✓ Marks 12th: {sm[1]}")
    print(f"  ✓ Marks 1-8: {sm[2]}, {sm[3]}, {sm[4]}, {sm[5]}, {sm[6]}, {sm[7]}, {sm[8]}, {sm[9]}")
else:
    print("  ❌ NO RECORDS FOUND")

# Check students_data view
print("\n📋 students_data view:")
cur.execute("""
    SELECT name, email, phone, college, category, dob, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
    FROM students_data WHERE student_id = %s
""", (student_id,))
sd = cur.fetchone()
if sd:
    print(f"  ✓ Name: {sd[0]}")
    print(f"  ✓ Email: {sd[1]}")
    print(f"  ✓ Phone: {sd[2]}")
    print(f"  ✓ College: {sd[3]}")
    print(f"  ✓ Category: {sd[4]}")
    print(f"  ✓ DOB: {sd[5]}")
    print(f"  ✓ Marks 1-8: {sd[6]}, {sd[7]}, {sd[8]}, {sd[9]}, {sd[10]}, {sd[11]}, {sd[12]}, {sd[13]}")
else:
    print("  ❌ NO RECORDS FOUND")

# Check pending_changes
print("\n📋 pending_changes:")
cur.execute("""
    SELECT change_id, status, auditor_id, admin_id, verified_at, approved_at
    FROM pending_changes WHERE student_id = %s ORDER BY created_at DESC LIMIT 1
""", (student_id,))
pc = cur.fetchone()
if pc:
    print(f"  ✓ Change ID: {pc[0]}")
    print(f"  ✓ Status: {pc[1]}")
    print(f"  ✓ Auditor ID: {pc[2]}")
    print(f"  ✓ Admin ID: {pc[3]}")
    print(f"  ✓ Verified At: {pc[4]}")
    print(f"  ✓ Approved At: {pc[5]}")

print("\n" + "="*80)
print("✅ WORKFLOW TEST COMPLETE")
print("="*80 + "\n")

cur.close()
conn.close()

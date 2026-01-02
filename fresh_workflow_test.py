#!/usr/bin/env python3
"""
Fresh test: Create a new student and test the complete workflow
"""
from db import get_connection
from datetime import datetime
import json

conn = get_connection()
cur = conn.cursor()

print("\n" + "="*80)
print("FRESH WORKFLOW TEST")
print("="*80)

# ============================================================================
# STEP 1: CREATE NEW TEST STUDENT
# ============================================================================
print("\n[STEP 1] Creating fresh test student...")

# Create a user
cur.execute("""
    INSERT INTO users_master (name, email, password, phone, address, category, dob, birth_place)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
""", (
    f"Fresh Test User",
    f"fresh_test_{datetime.now().timestamp()}@test.com",
    "hashed_password_test",
    "9999999999",
    "Fresh Test City",
    "General",
    "2000-01-01",
    "Fresh Birth Place"
))
user_id = cur.fetchone()[0]
print(f"✓ Created user: {user_id}")

# Create a student
cur.execute("""
    INSERT INTO students_master (user_id, current_status)
    VALUES (%s, %s)
    RETURNING id
""", (user_id, "active"))
student_id = cur.fetchone()[0]
print(f"✓ Created student: {student_id}")

conn.commit()

# ============================================================================
# STEP 2: SUBMIT EDIT REQUEST
# ============================================================================
print("\n[STEP 2] Submitting edit request...")

edit_data = {
    "name": "Fresh Updated",
    "email": "fresh_updated@test.com",
    "phone": "8888888888",
    "address": "Fresh Updated City",
    "marks_10th": 95,
    "marks_12th": 95,
    "marks1": 95,
    "marks2": 95,
    "marks3": 95,
    "marks4": 95,
    "marks5": 95,
    "marks6": 95,
    "marks7": 95,
    "marks8": 95
}

# Get current data as original
cur.execute("""
    SELECT 
        COALESCE(um.name, ''),
        COALESCE(um.email, ''),
        COALESCE(um.phone, ''),
        COALESCE(um.address, ''),
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
    LEFT JOIN users_master um ON st.user_id = um.id
    LEFT JOIN student_marks sm ON st.id = sm.student_id
    WHERE st.id = %s
""", (student_id,))

original_row = cur.fetchone()
original_data = {
    "name": original_row[0],
    "email": original_row[1],
    "phone": original_row[2],
    "address": original_row[3],
    "marks_10th": original_row[4],
    "marks_12th": original_row[5],
    "marks1": original_row[6],
    "marks2": original_row[7],
    "marks3": original_row[8],
    "marks4": original_row[9],
    "marks5": original_row[10],
    "marks6": original_row[11],
    "marks7": original_row[12],
    "marks8": original_row[13]
}

# Insert pending change
cur.execute("""
    INSERT INTO pending_changes (change_type, student_id, data, original_data, created_by, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
""", (
    "edit_student",
    student_id,
    json.dumps(edit_data),
    json.dumps(original_data),
    user_id,
    "pending"
))

change_id = cur.fetchone()[0]
conn.commit()
print(f"✓ Pending change created: {change_id}")

# ============================================================================
# STEP 3: AUDITOR VERIFICATION
# ============================================================================
print("\n[STEP 3] Auditor verification...")

auditor_user_id = user_id
cur.execute("""
    UPDATE pending_changes
    SET status = %s, auditor_id = %s, auditor_verified_at = CURRENT_TIMESTAMP
    WHERE id = %s
""", ("auditor_verified", auditor_user_id, change_id))

conn.commit()
print(f"✓ Change verified by auditor")

# ============================================================================
# STEP 4: ADMIN APPROVAL - DIRECT SQL
# ============================================================================
print("\n[STEP 4] Admin approval (direct SQL)...")

# Get the change
cur.execute("""
    SELECT data FROM pending_changes WHERE id = %s
""", (change_id,))

data_row = cur.fetchone()
if data_row:
    data = data_row[0]
    if isinstance(data, dict):
        change_data = data
    else:
        change_data = json.loads(data)
    
    print(f"  Processing {change_id}")
    print(f"  Marks in data: {change_data.get('marks1')}-{change_data.get('marks8')}")
    
    # Update users_master
    cur.execute("""
        UPDATE users_master
        SET name = %s, email = %s, phone = %s, address = %s
        WHERE id = %s
    """, (
        change_data.get("name"),
        change_data.get("email"),
        change_data.get("phone"),
        change_data.get("address"),
        user_id
    ))
    print(f"  ✓ users_master updated ({cur.rowcount} rows)")
    
    # Try UPDATE on student_marks
    print(f"  Attempting UPDATE on student_marks...")
    cur.execute("""
        UPDATE student_marks
        SET marks_10th = %s, marks_12th = %s, marks1 = %s, marks2 = %s, marks3 = %s, 
            marks4 = %s, marks5 = %s, marks6 = %s, marks7 = %s, marks8 = %s
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
    
    print(f"  UPDATE affected {cur.rowcount} rows")
    
    # If no rows, INSERT
    if cur.rowcount == 0:
        print(f"  No existing marks, INSERTing...")
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
        print(f"  ✓ INSERT successful ({cur.rowcount} rows)")
    
    # Mark as approved
    cur.execute("""
        UPDATE pending_changes
        SET status = %s, admin_id = %s, admin_approved_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, ("admin_approved", auditor_user_id, change_id))
    
    conn.commit()
    print(f"✓ Change marked as admin_approved")

# ============================================================================
# STEP 5: VERIFY RESULTS
# ============================================================================
print("\n[STEP 5] Verifying database results...")

print(f"\n  student_marks for {student_id}:")
cur.execute("""
    SELECT marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
    FROM student_marks WHERE student_id = %s
""", (student_id,))
marks_row = cur.fetchone()
if marks_row:
    print(f"  ✓ Marks 1-8: {marks_row[0]}, {marks_row[1]}, {marks_row[2]}, {marks_row[3]}, {marks_row[4]}, {marks_row[5]}, {marks_row[6]}, {marks_row[7]}")
else:
    print(f"  ❌ NO RECORD FOUND")

print(f"\n  students_data view for {student_id}:")
cur.execute("""
    SELECT name, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
    FROM students_data WHERE id = %s
""", (student_id,))
view_row = cur.fetchone()
if view_row:
    print(f"  ✓ Name: {view_row[0]}")
    print(f"  ✓ Marks 1-8: {view_row[1]}, {view_row[2]}, {view_row[3]}, {view_row[4]}, {view_row[5]}, {view_row[6]}, {view_row[7]}, {view_row[8]}")
else:
    print(f"  ❌ NO RECORD FOUND")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")

cur.close()
conn.close()

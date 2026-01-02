#!/usr/bin/env python3
"""
Debug script to verify data after admin approval
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
)
cur = conn.cursor()

print("\n" + "="*80)
print("CHECKING PENDING_CHANGES TABLE")
print("="*80)
cur.execute("""
    SELECT id, change_type, student_id, status, created_by, admin_id, admin_approved_at
    FROM pending_changes
    ORDER BY created_at DESC
    LIMIT 5
""")
changes = cur.fetchall()
for row in changes:
    print(f"Change ID: {row[0]}")
    print(f"  Type: {row[1]}")
    print(f"  Student ID: {row[2]}")
    print(f"  Status: {row[3]}")
    print(f"  Created By: {row[4]}")
    print(f"  Admin ID: {row[5]}")
    print(f"  Admin Approved At: {row[6]}")
    print()

# Get the latest admin_approved change
cur.execute("""
    SELECT id, student_id, data
    FROM pending_changes
    WHERE status = 'admin_approved'
    ORDER BY admin_approved_at DESC
    LIMIT 1
""")
latest_approved = cur.fetchone()

if latest_approved:
    print("\n" + "="*80)
    print("LATEST ADMIN-APPROVED CHANGE")
    print("="*80)
    change_id, student_id, data = latest_approved
    print(f"Change ID: {change_id}")
    print(f"Student ID: {student_id}")
    print(f"Proposed Data: {data}")
    
    print("\n" + "="*80)
    print(f"CHECKING DATABASE FOR STUDENT {student_id}")
    print("="*80)
    
    # Check users_master
    cur.execute("""
        SELECT id, name, email, phone, address, category, dob, birth_place
        FROM users_master
        WHERE id = (SELECT user_id FROM students_master WHERE id = %s)
    """, (student_id,))
    user_data = cur.fetchone()
    if user_data:
        print("users_master:")
        print(f"  ID: {user_data[0]}")
        print(f"  Name: {user_data[1]}")
        print(f"  Email: {user_data[2]}")
        print(f"  Phone: {user_data[3]}")
        print(f"  Address (College): {user_data[4]}")
        print(f"  Category: {user_data[5]}")
        print(f"  DOB: {user_data[6]}")
        print(f"  Birth Place: {user_data[7]}")
    
    # Check student_marks
    cur.execute("""
        SELECT marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
        FROM student_marks
        WHERE student_id = %s
    """, (student_id,))
    marks = cur.fetchone()
    if marks:
        print("\nstudent_marks:")
        print(f"  10th: {marks[0]}, 12th: {marks[1]}")
        print(f"  Sem 1-4: {marks[2]}, {marks[3]}, {marks[4]}, {marks[5]}")
        print(f"  Sem 5-8: {marks[6]}, {marks[7]}, {marks[8]}, {marks[9]}")
    else:
        print("\nstudent_marks: NO RECORDS FOUND")
    
    # Check what students_data view returns
    print("\n" + "="*80)
    print("STUDENTS_DATA VIEW OUTPUT")
    print("="*80)
    cur.execute("""
        SELECT name, email, phone, college, category, dob, marks1, marks2, marks3, marks4
        FROM students_data
        WHERE id = %s
    """, (student_id,))
    view_data = cur.fetchone()
    if view_data:
        print(f"  Name: {view_data[0]}")
        print(f"  Email: {view_data[1]}")
        print(f"  Phone: {view_data[2]}")
        print(f"  College: {view_data[3]}")
        print(f"  Category: {view_data[4]}")
        print(f"  DOB: {view_data[5]}")
        print(f"  Marks 1-4: {view_data[6]}, {view_data[7]}, {view_data[8]}, {view_data[9]}")
    else:
        print("  NO DATA IN VIEW")

print("\n" + "="*80)
print("END DEBUG")
print("="*80)

cur.close()
conn.close()

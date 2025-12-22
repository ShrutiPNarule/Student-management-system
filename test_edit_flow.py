#!/usr/bin/env python
"""Test the edit approval flow"""
from db import get_connection
import json

conn = get_connection()
cur = conn.cursor()

try:
    # Get a student
    cur.execute("SELECT id, user_id FROM students_master LIMIT 1")
    result = cur.fetchone()
    
    if not result:
        print("❌ No students found in database")
        cur.close()
        conn.close()
        exit(1)
    
    student_id, user_id = result
    print(f"✅ Found student: {student_id}, user_id: {user_id}")
    
    # Get an admin
    cur.execute("SELECT id FROM users_master WHERE id LIKE 'US%' LIMIT 1")
    admin_result = cur.fetchone()
    
    if not admin_result:
        print("❌ No users found in database")
        cur.close()
        conn.close()
        exit(1)
    
    admin_id = admin_result[0]
    print(f"✅ Using admin ID: {admin_id}")
    
    # Test the insert query
    action_data = {
        "name": "Test Name",
        "enrollment_no": "ENR001",
        "college": "Test College",
        "phone": "9876543210",
        "email": "test@test.com",
        "marks_10th": 95,
        "marks_12th": 90,
        "marks1": 85,
        "marks2": 80,
        "marks3": 75,
        "marks4": 70
    }
    
    print(f"\n🔍 Testing INSERT query...")
    cur.execute("""
        INSERT INTO admin_approval_requests 
        (admin_id, request_type, entity_type, entity_id, action_data, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (admin_id, "EDIT", "STUDENT", student_id, json.dumps(action_data), "pending"))
    
    conn.commit()
    print("✅ Insert successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    if hasattr(e, 'pgcode'):
        print(f"PG Error Code: {e.pgcode}")
    if hasattr(e, 'pgerror'):
        print(f"PG Error Detail: {e.pgerror}")
    conn.rollback()

finally:
    cur.close()
    conn.close()

#!/usr/bin/env python3
"""
Backfill marks for previously approved changes that didn't get marks inserted
"""
from db import get_connection
import json

conn = get_connection()
cur = conn.cursor()

print("\n=== BACKFILLING MARKS FOR PREVIOUS APPROVALS ===\n")

# Find all admin_approved changes that have marks in data but not in student_marks table
cur.execute("""
    SELECT pc.id, pc.student_id, pc.data
    FROM pending_changes pc
    WHERE pc.status = 'admin_approved'
    AND NOT EXISTS (SELECT 1 FROM student_marks sm WHERE sm.student_id = pc.student_id)
    ORDER BY pc.id
""")

pending_changes = cur.fetchall()

for pc_id, student_id, data in pending_changes:
    if isinstance(data, dict):
        change_data = data
    else:
        change_data = json.loads(data)
    
    # Check if data has marks
    if any(key in change_data for key in ['marks1', 'marks2', 'marks3', 'marks4', 'marks5', 'marks6', 'marks7', 'marks8']):
        print(f"Processing {pc_id} for student {student_id}...")
        
        try:
            # Insert marks
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
            conn.commit()
            print(f"  ✓ Inserted marks for {pc_id}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            conn.rollback()
    else:
        print(f"Skipping {pc_id} - no marks data")

print("\n=== BACKFILL COMPLETE ===\n")

# Verify
print("Final status:")
cur.execute("""
    SELECT pc.id, pc.student_id, 
           CASE WHEN sm.id IS NOT NULL THEN 'HAS MARKS' ELSE 'NO MARKS' END AS status
    FROM pending_changes pc
    LEFT JOIN student_marks sm ON pc.student_id = sm.student_id
    WHERE pc.status = 'admin_approved'
    ORDER BY pc.id
""")

for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} - {row[2]}")

cur.close()
conn.close()

#!/usr/bin/env python3
"""
Clean up duplicate student_marks records
"""
from db import get_connection

conn = get_connection()
cur = conn.cursor()

print("\n=== CLEANING UP DUPLICATE MARKS RECORDS ===\n")

# Find students with multiple marks records
cur.execute("""
    SELECT student_id, COUNT(*) as count
    FROM student_marks
    GROUP BY student_id
    HAVING COUNT(*) > 1
    ORDER BY student_id
""")

duplicates = cur.fetchall()
print(f"Found {len(duplicates)} students with duplicate records:\n")

for student_id, count in duplicates:
    print(f"{student_id}: {count} records")
    
    # Get the latest approved change for this student
    cur.execute("""
        SELECT id, data FROM pending_changes
        WHERE student_id = %s AND status = 'admin_approved'
        ORDER BY admin_approved_at DESC LIMIT 1
    """, (student_id,))
    
    latest_pc = cur.fetchone()
    if latest_pc:
        latest_data = latest_pc[1]
        import json
        if isinstance(latest_data, dict):
            change_data = latest_data
        else:
            change_data = json.loads(latest_data)
        
        print(f"  Latest approved data has marks: {change_data.get('marks1')}, {change_data.get('marks2')}, ..., {change_data.get('marks8')}")
        
        # Delete all marks records for this student
        cur.execute("DELETE FROM student_marks WHERE student_id = %s", (student_id,))
        print(f"  Deleted all {cur.rowcount} records")
        
        # Insert the correct one based on latest approved change
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
        print(f"  Inserted 1 correct record with latest approved marks\n")
    
    conn.commit()

print("=== CLEANUP COMPLETE ===\n")

# Verify
print("Final check:")
cur.execute("SELECT student_id, COUNT(*) as count FROM student_marks GROUP BY student_id HAVING COUNT(*) > 1")
remaining = cur.fetchall()
if remaining:
    print(f"❌ Still {len(remaining)} students with duplicates:")
    for r in remaining:
        print(f"  {r[0]}: {r[1]} records")
else:
    print("✓ No duplicates remaining")

cur.close()
conn.close()

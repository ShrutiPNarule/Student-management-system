from db import get_connection
import json

conn = get_connection()
cur = conn.cursor()

print("\n=== CHECKING PC000003 (ST000002) ===")

# Get pending changes data
cur.execute("SELECT id, data, student_id FROM pending_changes WHERE id = 'PC000003'")
pc = cur.fetchone()
if pc:
    pc_id, data, student_id = pc
    if isinstance(data, dict):
        pc_data = data
    else:
        pc_data = json.loads(data)
    
    print(f"\nPending Change Data:")
    print(f"  PC ID: {pc_id}")
    print(f"  Student ID: {student_id}")
    print(f"  Marks in PC: {pc_data.get('marks1')}, {pc_data.get('marks2')}, ..., {pc_data.get('marks8')}")

# Get student record
cur.execute("SELECT name FROM users_master WHERE id = (SELECT user_id FROM students_master WHERE id = %s)", (student_id,))
user = cur.fetchone()
if user:
    print(f"  Student Name: {user[0]}")

# Get student_marks
print(f"\nstudent_marks for {student_id}:")
cur.execute("SELECT id, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8 FROM student_marks WHERE student_id = %s", (student_id,))
marks = cur.fetchone()
if marks:
    print(f"  ID: {marks[0]}")
    print(f"  Marks 1-8: {marks[1]}, {marks[2]}, {marks[3]}, {marks[4]}, {marks[5]}, {marks[6]}, {marks[7]}, {marks[8]}")
else:
    print("  NO RECORD FOUND")

# Get students_data view
print(f"\nstudents_data view for {student_id}:")
cur.execute("SELECT name, email, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8 FROM students_data WHERE id = %s", (student_id,))
view_row = cur.fetchone()
if view_row:
    print(f"  Name: {view_row[0]}")
    print(f"  Email: {view_row[1]}")
    print(f"  Marks 1-8: {view_row[2]}, {view_row[3]}, {view_row[4]}, {view_row[5]}, {view_row[6]}, {view_row[7]}, {view_row[8]}, {view_row[9]}")
else:
    print("  NO RECORD FOUND")

cur.close()
conn.close()

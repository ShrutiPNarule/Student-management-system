from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute('SELECT id, student_id, marks1 FROM student_marks WHERE student_id = %s', ('ST000002',))
rows = cur.fetchall()
print(f"Records for ST000002: {len(rows)} record(s)")
for row in rows:
    print(f"  ID {row[0]}: marks1={row[2]}")

# Check the view
cur.execute('SELECT id, name, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8 FROM students_data WHERE id = %s', ('ST000002',))
view_row = cur.fetchone()
if view_row:
    print(f"\nstudents_data for ST000002:")
    print(f"  Name: {view_row[1]}")
    print(f"  Marks 1-8: {view_row[2]}, {view_row[3]}, {view_row[4]}, {view_row[5]}, {view_row[6]}, {view_row[7]}, {view_row[8]}, {view_row[9]}")

cur.close()
conn.close()

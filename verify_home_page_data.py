from db import get_connection

conn = get_connection()
cur = conn.cursor()

print("\n=== HOME PAGE DATA VERIFICATION ===\n")

# Check what would be displayed on the home page
cur.execute("""
    SELECT id, name, email, phone, college, category, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
    FROM students_data
    WHERE id IN ('ST000002', 'ST000003', 'ST000009')
    ORDER BY id
""")

for row in cur.fetchall():
    student_id = row[0]
    name = row[1]
    email = row[2]
    phone = row[3]
    college = row[4]
    category = row[5]
    marks = row[6:14]
    
    print(f"\n{student_id}: {name}")
    print(f"  Email: {email}")
    print(f"  Phone: {phone}")
    print(f"  College: {college}")
    print(f"  Category: {category}")
    print(f"  Marks: {marks[0]}, {marks[1]}, {marks[2]}, {marks[3]}, {marks[4]}, {marks[5]}, {marks[6]}, {marks[7]}")

cur.close()
conn.close()

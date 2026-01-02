from db import get_connection

conn = get_connection()
cur = conn.cursor()

print("\n=== STUDENT_MARKS COLUMNS ===")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='student_marks'")
cols = [row[0] for row in cur.fetchall()]
print(cols)

print("\n=== SAMPLE STUDENT_MARKS ===")
cur.execute("SELECT * FROM student_marks LIMIT 1")
row = cur.fetchone()
if row:
    for col, val in zip(cols, row):
        print(f"{col}: {val}")
else:
    print("No records found")

cur.close()
conn.close()

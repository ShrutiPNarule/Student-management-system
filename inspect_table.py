from db import get_connection

conn = get_connection()
cur = conn.cursor()

print("\n=== STUDENTS_MASTER COLUMNS ===")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='students_master'")
print([row[0] for row in cur.fetchall()])

print("\n=== STUDENTS_MASTER SAMPLE ===")
cur.execute("SELECT * FROM students_master LIMIT 1")
cols = [d[0] for d in cur.description]
row = cur.fetchone()
if row:
    for col, val in zip(cols, row):
        print(f"{col}: {val}")

cur.close()
conn.close()

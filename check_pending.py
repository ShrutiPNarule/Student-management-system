from db import get_connection
import json

conn = get_connection()
cur = conn.cursor()

print("\n=== PENDING_CHANGES TABLE ===")
cur.execute("SELECT * FROM pending_changes WHERE status != 'pending' LIMIT 1")
row = cur.fetchone()

if row:
    cols = [d[0] for d in cur.description]
    for col, val in zip(cols, row):
        if col in ['data', 'original_data']:
            if isinstance(val, dict):
                print(f"{col}: {json.dumps(val, indent=2)}")
            else:
                print(f"{col}: {val}")
        else:
            print(f"{col}: {val}")
else:
    print("No pending_changes records found")

print("\n=== LATEST PENDING CHANGES ===")
cur.execute("""
    SELECT id, change_type, student_id, status, created_at 
    FROM pending_changes 
    ORDER BY created_at DESC LIMIT 5
""")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]} {row[2]} - {row[3]} ({row[4]})")

cur.close()
conn.close()

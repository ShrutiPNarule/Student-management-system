from db import get_connection

# Test if approval_seq exists
conn = get_connection()
cur = conn.cursor()

# Check sequence
try:
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'approval_seq')")
    exists = cur.fetchone()[0]
    print(f"[TEST] approval_seq exists: {exists}")
    
    # Check admin_approval_requests table
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'admin_approval_requests'
    """)
    columns = cur.fetchall()
    print(f"[TEST] admin_approval_requests columns: {columns}")
    
    # Try to insert a test record
    print("[TEST] Attempting to insert test approval request...")
    cur.execute("""
        INSERT INTO admin_approval_requests 
        (admin_id, request_type, entity_type, entity_id, action_data, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, ("US000001", "EDIT", "STUDENT", "ST000001", '{"test": "data"}', "pending"))
    conn.commit()
    print("[TEST] Insert successful!")
    
    # Check what was inserted
    cur.execute("SELECT id FROM admin_approval_requests ORDER BY id DESC LIMIT 1")
    result = cur.fetchone()
    print(f"[TEST] Last inserted ID: {result[0] if result else 'No records'}")
    
except Exception as e:
    print(f"[TEST ERROR] {type(e).__name__}: {e}")
finally:
    cur.close()
    conn.close()

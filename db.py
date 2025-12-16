import psycopg2
import os
import sys

# =========================
# DB CONNECTION
# =========================
try:
    conn = psycopg2.connect(
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
    )
except Exception as e:
    print(f"[DB ERROR] Unable to connect: {e}")
    sys.exit(1)

cur = conn.cursor()

# =========================
# SEQUENCES
# =========================
cur.execute("CREATE SEQUENCE IF NOT EXISTS role_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS user_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS school_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS college_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS subject_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS activity_seq START 1;")

# =========================
# MASTER TABLES
# =========================

# ---- ROLES ----
cur.execute("""
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY DEFAULT
        'RL' || LPAD(nextval('role_seq')::TEXT, 4, '0'),
    name TEXT UNIQUE NOT NULL
);
""")

# ---- USERS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT
        'US' || LPAD(nextval('user_seq')::TEXT, 6, '0'),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone VARCHAR(15),
    role_id TEXT REFERENCES roles(id) ON DELETE SET NULL,
    dob DATE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- SCHOOLS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS schools (
    id TEXT PRIMARY KEY DEFAULT
        'SC' || LPAD(nextval('school_seq')::TEXT, 5, '0'),
    name TEXT NOT NULL,
    address TEXT,
    district TEXT,
    state TEXT,
    board TEXT
);
""")

# ---- COLLEGES ----
cur.execute("""
CREATE TABLE IF NOT EXISTS colleges (
    id TEXT PRIMARY KEY DEFAULT
        'CL' || LPAD(nextval('college_seq')::TEXT, 5, '0'),
    aicte_id TEXT UNIQUE,
    name TEXT NOT NULL,
    address TEXT,
    district TEXT,
    state TEXT,
    institute_type TEXT,
    is_women BOOLEAN DEFAULT FALSE,
    is_minority BOOLEAN DEFAULT FALSE
);
""")

# ---- SUBJECTS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY DEFAULT
        'SB' || LPAD(nextval('subject_seq')::TEXT, 5, '0'),
    name TEXT NOT NULL,
    credits INTEGER,
    semester INTEGER
);
""")

# =========================
# ACTIVITY LOG (IMPORTANT)
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS activity_log (
    id TEXT PRIMARY KEY DEFAULT
        'AL' || LPAD(nextval('activity_seq')::TEXT, 6, '0'),
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    metadata JSONB,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# =========================
# COMMIT
# =========================
conn.commit()

# =========================
# HELPERS
# =========================
def get_connection():
    return conn

def get_cursor():
    return cur

def close_connection():
    cur.close()
    conn.close()

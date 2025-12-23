import psycopg2
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =========================
# DB CONNECTION
# =========================
try:
    conn = psycopg2.connect(
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        connect_timeout=5
    )
    print("[DB] ✅ Database connection established")
except Exception as e:
    print(f"[DB ERROR] Unable to connect: {e}")
    print(f"[DB ERROR] Attempted connection with:")
    print(f"  - Database: {os.getenv('DB_DATABASE')}")
    print(f"  - User: {os.getenv('DB_USER')}")
    print(f"  - Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  - Port: {os.getenv('DB_PORT', '5432')}")
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
cur.execute("CREATE SEQUENCE IF NOT EXISTS student_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS mark_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS enrollment_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS school_history_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS college_subject_seq START 1;")
cur.execute("CREATE SEQUENCE IF NOT EXISTS activity_seq START 1;")

# =========================
# MASTER TABLES
# =========================

# ---- ROLES MASTER (WITH PERMISSIONS) ----
cur.execute("""
CREATE TABLE IF NOT EXISTS roles_master (
    id TEXT PRIMARY KEY DEFAULT
        'RL' || LPAD(nextval('role_seq')::TEXT, 4, '0'),
    name TEXT UNIQUE NOT NULL,

    view_student BOOLEAN DEFAULT FALSE,
    add_student BOOLEAN DEFAULT FALSE,
    delete_student BOOLEAN DEFAULT FALSE,
    change_user_role BOOLEAN DEFAULT FALSE,
    add_marks BOOLEAN DEFAULT FALSE,
    view_activity_log BOOLEAN DEFAULT FALSE,
    create_application BOOLEAN DEFAULT FALSE,
    approve_application BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- USERS MASTER ----
cur.execute("""
CREATE TABLE IF NOT EXISTS users_master (
    id TEXT PRIMARY KEY DEFAULT
        'US' || LPAD(nextval('user_seq')::TEXT, 6, '0'),
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone VARCHAR(15),
    role_id TEXT REFERENCES roles_master(id) ON DELETE SET NULL,
    dob DATE,
    address TEXT,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Add new columns to users_master if they don't exist
try:
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS religion VARCHAR(50);")
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS category VARCHAR(50);")
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS caste VARCHAR(50);")
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS birth_place VARCHAR(100);")
except:
    pass

# ---- SCHOOLS MASTER ----
cur.execute("""
CREATE TABLE IF NOT EXISTS schools_master (
    id TEXT PRIMARY KEY DEFAULT
        'SC' || LPAD(nextval('school_seq')::TEXT, 5, '0'),
    name TEXT NOT NULL,
    address TEXT,
    district TEXT,
    state TEXT,
    board TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- COLLEGES MASTER ----
cur.execute("""
CREATE TABLE IF NOT EXISTS colleges_master (
    id TEXT PRIMARY KEY DEFAULT
        'CL' || LPAD(nextval('college_seq')::TEXT, 5, '0'),
    aicte_id TEXT UNIQUE,
    name TEXT NOT NULL,
    address TEXT,
    district TEXT,
    state TEXT,
    institute_type TEXT,
    is_women BOOLEAN DEFAULT FALSE,
    is_minority BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- SUBJECTS MASTER ----
cur.execute("""
CREATE TABLE IF NOT EXISTS subjects_master (
    id TEXT PRIMARY KEY DEFAULT
        'SB' || LPAD(nextval('subject_seq')::TEXT, 5, '0'),
    name TEXT NOT NULL,
    semester INTEGER,
    credits INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# =========================
# STUDENT MANAGEMENT
# =========================

# ---- STUDENTS MASTER ----
cur.execute("""
CREATE TABLE IF NOT EXISTS students_master (
    id TEXT PRIMARY KEY DEFAULT
        'ST' || LPAD(nextval('student_seq')::TEXT, 6, '0'),
    user_id TEXT REFERENCES users_master(id) ON DELETE SET NULL,
    enrollment_no VARCHAR(30) UNIQUE,
    current_status VARCHAR(20),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- STUDENT SCHOOL HISTORY ----
cur.execute("""
CREATE TABLE IF NOT EXISTS student_school_history (
    id TEXT PRIMARY KEY DEFAULT
        'SH' || LPAD(nextval('school_history_seq')::TEXT, 6, '0'),
    student_id TEXT NOT NULL REFERENCES students_master(id) ON DELETE CASCADE,
    school_id TEXT NOT NULL REFERENCES schools_master(id) ON DELETE CASCADE,
    year_of_passing INTEGER,
    percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- COLLEGE ENROLLMENT ----
cur.execute("""
CREATE TABLE IF NOT EXISTS college_enrollment (
    id TEXT PRIMARY KEY DEFAULT
        'EN' || LPAD(nextval('enrollment_seq')::TEXT, 6, '0'),
    student_id TEXT NOT NULL REFERENCES students_master(id) ON DELETE CASCADE,
    college_id TEXT NOT NULL REFERENCES colleges_master(id) ON DELETE CASCADE,
    admission_year INTEGER,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- COLLEGE SUBJECTS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS college_subjects (
    id TEXT PRIMARY KEY DEFAULT
        'CS' || LPAD(nextval('college_subject_seq')::TEXT, 6, '0'),
    college_id TEXT NOT NULL REFERENCES colleges_master(id) ON DELETE CASCADE,
    subject_id TEXT NOT NULL REFERENCES subjects_master(id) ON DELETE CASCADE,
    semester INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- MARKS ----
cur.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id TEXT PRIMARY KEY DEFAULT
        'MK' || LPAD(nextval('mark_seq')::TEXT, 6, '0'),
    student_id TEXT NOT NULL REFERENCES students_master(id) ON DELETE CASCADE,
    subject_id TEXT NOT NULL REFERENCES subjects_master(id) ON DELETE CASCADE,
    marks INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---- STUDENT MARKS (for storing marks by year) ----
cur.execute("""
CREATE TABLE IF NOT EXISTS student_marks (
    id SERIAL PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students_master(id) ON DELETE CASCADE,
    marks_10th INTEGER,
    marks_12th INTEGER,
    marks1 INTEGER,
    marks2 INTEGER,
    marks3 INTEGER,
    marks4 INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# =========================
# ADMIN APPROVAL REQUESTS
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS admin_approval_requests (
    id TEXT PRIMARY KEY DEFAULT
        'AR' || LPAD(nextval('activity_seq')::TEXT, 6, '0'),
    admin_id TEXT NOT NULL REFERENCES users_master(id) ON DELETE CASCADE,
    request_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action_data JSONB,
    status TEXT DEFAULT 'pending',
    approval_notes TEXT,
    approved_by TEXT REFERENCES users_master(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP DEFAULT NULL
);
""")

# =========================
# ACTIVITY LOG
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS activity_log (
    id TEXT PRIMARY KEY DEFAULT
        'AL' || LPAD(nextval('activity_seq')::TEXT, 6, '0'),
    user_id TEXT REFERENCES users_master(id) ON DELETE SET NULL,
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
    try:
        return psycopg2.connect(
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
        )
    except Exception as e:
        print(f"[DB ERROR] Unable to create connection: {e}")
        return None

def close_connection():
    cur.close()
    conn.close()

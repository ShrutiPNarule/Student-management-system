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
    print("[DB] [OK] Database connection established")
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
cur.execute("CREATE SEQUENCE IF NOT EXISTS approval_seq START 1;")

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
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;")
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS deleted_by TEXT REFERENCES users_master(id) ON DELETE SET NULL;")
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;")
    cur.execute("ALTER TABLE users_master ADD COLUMN IF NOT EXISTS deletion_reason TEXT;")
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
        'AR' || LPAD(nextval('approval_seq')::TEXT, 6, '0'),
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
# ATTENDANCE RECORDS TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance_records (
    id SERIAL PRIMARY KEY,
    student_id TEXT REFERENCES students_master(id) ON DELETE CASCADE,
    attendance_month DATE NOT NULL,
    present_days INTEGER DEFAULT 0,
    absent_days INTEGER DEFAULT 0,
    leave_days INTEGER DEFAULT 0,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, attendance_month)
);
""")

# =========================
# SCHOLARSHIPS TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS scholarships (
    id SERIAL PRIMARY KEY,
    student_id TEXT REFERENCES students_master(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    amount DECIMAL(10, 2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    provider TEXT,
    status TEXT CHECK (status IN ('active', 'inactive', 'completed', 'pending')),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# =========================
# STUDENT DOCUMENTS TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS student_documents (
    id SERIAL PRIMARY KEY,
    student_id TEXT REFERENCES students_master(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT,
    issue_date DATE,
    expiry_date DATE,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# =========================
# NOTIFICATION PREFERENCES TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE REFERENCES users_master(id) ON DELETE CASCADE,
    email_approvals BOOLEAN DEFAULT TRUE,
    email_approvals_completed BOOLEAN DEFAULT TRUE,
    email_daily_summary BOOLEAN DEFAULT FALSE,
    sms_approvals BOOLEAN DEFAULT FALSE,
    sms_phone TEXT,
    notification_frequency TEXT DEFAULT 'instant' CHECK (notification_frequency IN ('instant', 'hourly', 'daily')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# =========================
# STUDENTS DATA VIEW
# =========================
# This view provides a unified interface for accessing student information
cur.execute("""
DROP VIEW IF EXISTS students_data CASCADE;
""")

cur.execute("""
CREATE VIEW students_data AS
SELECT 
    sm.id,
    COALESCE(um.name, '') AS name,
    COALESCE(sm.enrollment_no, '') AS roll_no,
    COALESCE(um.address, '') AS address,
    COALESCE(um.phone, '') AS phone,
    COALESCE(um.email, '') AS email,
    COALESCE(cc.name, '') AS college,
    COALESCE(um.category, 'General') AS category,
    COALESCE(um.dob::TEXT, '') AS dob,
    COALESCE(sm.current_status, 'Active') AS status,
    COALESCE(sm1.marks_10th, 0) AS marks_10th,
    COALESCE(sm1.marks_12th, 0) AS marks_12th,
    COALESCE(sm1.marks1, 0) AS marks1,
    COALESCE(sm1.marks2, 0) AS marks2,
    COALESCE(sm1.marks3, 0) AS marks3,
    COALESCE(sm1.marks4, 0) AS marks4,
    COALESCE(sm1.marks5, 0) AS marks5,
    COALESCE(sm1.marks6, 0) AS marks6,
    COALESCE(sm1.marks7, 0) AS marks7,
    COALESCE(sm1.marks8, 0) AS marks8,
    CASE 
        WHEN sm1.marks1 > 0 OR sm1.marks2 > 0 OR sm1.marks3 > 0 OR sm1.marks4 > 0 OR 
             sm1.marks5 > 0 OR sm1.marks6 > 0 OR sm1.marks7 > 0 OR sm1.marks8 > 0
        THEN ROUND((COALESCE(sm1.marks1, 0) + COALESCE(sm1.marks2, 0) + 
                    COALESCE(sm1.marks3, 0) + COALESCE(sm1.marks4, 0) +
                    COALESCE(sm1.marks5, 0) + COALESCE(sm1.marks6, 0) + 
                    COALESCE(sm1.marks7, 0) + COALESCE(sm1.marks8, 0))::NUMERIC / 8, 2)
        ELSE 0
    END AS gpa,
    sm.created_at
FROM 
    students_master sm
LEFT JOIN users_master um ON sm.user_id = um.id
LEFT JOIN college_enrollment ce ON sm.id = ce.student_id
LEFT JOIN colleges_master cc ON ce.college_id = cc.id
LEFT JOIN student_marks sm1 ON sm.id = sm1.student_id
WHERE sm.is_deleted = FALSE;
""")

# =========================
# IP WHITELIST TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS ip_whitelist (
    id TEXT PRIMARY KEY DEFAULT
        'IP' || LPAD(nextval('activity_seq')::TEXT, 6, '0'),
    ip_address VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    added_by TEXT REFERENCES users_master(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# =========================
# ACTIVE SESSIONS TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS active_sessions (
    id TEXT PRIMARY KEY DEFAULT
        'SS' || LPAD(nextval('activity_seq')::TEXT, 6, '0'),
    user_id TEXT NOT NULL REFERENCES users_master(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
""")

# =========================
# SECURITY CONFIGURATION TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS security_config (
    id TEXT PRIMARY KEY DEFAULT
        'SC' || LPAD(nextval('activity_seq')::TEXT, 6, '0'),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    setting_type VARCHAR(20) DEFAULT 'string',
    updated_by TEXT REFERENCES users_master(id) ON DELETE SET NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Insert default security settings
cur.execute("""
INSERT INTO security_config (setting_key, setting_value, description, setting_type)
VALUES 
    ('password_min_length', '8', 'Minimum password length', 'integer'),
    ('password_require_uppercase', 'true', 'Require uppercase letters in password', 'boolean'),
    ('password_require_numbers', 'true', 'Require numbers in password', 'boolean'),
    ('password_require_special', 'true', 'Require special characters in password', 'boolean'),
    ('password_expiration_days', '90', 'Password expiration in days (0 = never)', 'integer'),
    ('failed_login_attempts', '5', 'Max failed login attempts before lockout', 'integer'),
    ('lockout_duration_minutes', '15', 'Account lockout duration in minutes', 'integer'),
    ('session_timeout_minutes', '30', 'Session timeout in minutes of inactivity', 'integer'),
    ('enable_2fa', 'true', 'Enable two-factor authentication', 'boolean'),
    ('enable_ip_whitelist', 'false', 'Enforce IP whitelist', 'boolean'),
    ('audit_log_retention_days', '180', 'Audit log retention in days', 'integer'),
    ('enable_email_verification', 'true', 'Require email verification for new accounts', 'boolean'),
    ('suspicious_login_alert', 'true', 'Alert on suspicious login attempts', 'boolean'),
    ('api_rate_limit', '100', 'API calls per minute per user', 'integer')
ON CONFLICT (setting_key) DO NOTHING;
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

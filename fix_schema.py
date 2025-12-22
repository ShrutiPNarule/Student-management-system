import psycopg2
import os
import sys

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

# Drop dependent tables in correct order
print("Dropping old tables...")
tables_to_drop = [
    "marks",
    "college_subjects",
    "college_enrollment",
    "student_school_history",
    "students_master",
]

for table in tables_to_drop:
    try:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        print(f"  ✓ Dropped {table}")
    except Exception as e:
        print(f"  ✗ Error dropping {table}: {e}")

conn.commit()

print("\nCreating sequences...")
sequences = [
    "student_seq",
    "school_history_seq",
    "enrollment_seq",
    "college_subject_seq",
    "mark_seq",
]
for seq in sequences:
    try:
        cur.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq} START 1;")
        print(f"  ✓ Created {seq}")
    except Exception as e:
        print(f"  ✗ Error creating {seq}: {e}")

conn.commit()

print("\nRecreating tables with correct schema...")

# ---- STUDENTS MASTER ----
cur.execute("""
CREATE TABLE IF NOT EXISTS students_master (
    id TEXT PRIMARY KEY DEFAULT
        'ST' || LPAD(nextval('student_seq')::TEXT, 6, '0'),
    user_id TEXT REFERENCES users_master(id) ON DELETE SET NULL,
    enrollment_no VARCHAR(30) UNIQUE,
    current_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
print("  ✓ Created students_master")

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
print("  ✓ Created student_school_history")

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
print("  ✓ Created college_enrollment")

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
print("  ✓ Created college_subjects")

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
print("  ✓ Created marks")

conn.commit()
print("\n✓ Schema migration completed successfully!")
cur.close()
conn.close()

CREATE TABLE students_master (
   id          SERIAL PRIMARY KEY,
   name        VARCHAR(100) NOT NULL,
   roll_no     VARCHAR(20) UNIQUE NOT NULL,
   college     VARCHAR(100),
   phone       VARCHAR(20),
   email       VARCHAR(100)
);

CREATE TABLE student_marks (
    id          SERIAL PRIMARY KEY,
   student_id  INT NOT NULL REFERENCES students_master(id) ON DELETE CASCADE,
    marks_10th  INT,
    marks_12th  INT,
    marks_year1 INT,
    marks_year2 INT,
    marks_year3 INT,
    marks_year4 INT
);

ALTER TABLE student_marks RENAME COLUMN marks_year1 TO marks1;
ALTER TABLE student_marks RENAME COLUMN marks_year2 TO marks2;
ALTER TABLE student_marks RENAME COLUMN marks_year3 TO marks3;
ALTER TABLE student_marks RENAME COLUMN marks_year4 TO marks4;

SELECT * FROM students_master;

SELECT * FROM student_marks;

DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


SELECT * FROM users;

TRUNCATE TABLE users;

DROP TABLE users;

SELECT *
FROM students_master
JOIN student_marks
ON students_master.id = student_marks.student_id;


SELECT *
FROM students_master
LEFT JOIN student_marks
ON students_master.id = student_marks.student_id;

CREATE TABLE admission_details (
    id              SERIAL PRIMARY KEY,
    student_id      INT NOT NULL REFERENCES students_master(id) ON DELETE CASCADE,
    marks_id        INT UNIQUE REFERENCES student_marks(id) ON DELETE SET NULL,
    
    course          VARCHAR(100) NOT NULL,
    branch          VARCHAR(100),
    academic_year   VARCHAR(9),              -- e.g. '2024-25'
    admission_date  DATE NOT NULL,
    admission_quota VARCHAR(50),             -- e.g. 'CAP', 'Management', 'SC/ST'
    fees            NUMERIC(10,2),
    status          VARCHAR(20) DEFAULT 'active',  -- 'active', 'cancelled', 'passed_out'
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE admission_details
ADD CONSTRAINT unique_admission_per_student UNIQUE (student_id);

CREATE TABLE roles (
    role_id           SERIAL PRIMARY KEY,
    role_name         VARCHAR(50) UNIQUE NOT NULL,
    priority          INT NOT NULL,          -- higher = more powerful
    can_manage_users  BOOLEAN DEFAULT FALSE,
    can_manage_data   BOOLEAN DEFAULT FALSE,
    can_view_logs     BOOLEAN DEFAULT FALSE
);

INSERT INTO roles (role_name, priority, can_manage_users, can_manage_data, can_view_logs)
VALUES
    ('super_admin', 3, TRUE,  FALSE, TRUE),  -- manages users + monitors, rarely edits data
    ('admin',       2, FALSE, TRUE,  TRUE),  -- manages data + sees user activity
    ('general',     1, FALSE, FALSE, FALSE); -- normal user
	
-- Then link it to your existing users table`
ALTER TABLE users
ADD COLUMN role_id INT REFERENCES roles(role_id);

-- Set default role for existing users (probably general)
UPDATE users
SET role_id = (SELECT role_id FROM roles WHERE role_name = 'general')
WHERE role_id IS NULL;
-- Adding table activity log  - This is how Super Admin monitors Admin, and Admin monitors general users
CREATE TABLE activity_logs (
    log_id      SERIAL PRIMARY KEY,
    user_email  VARCHAR(255) NOT NULL,
    role_name   VARCHAR(50) NOT NULL,
    action      VARCHAR(255) NOT NULL,
    details     TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP


-- Soft delete = columns, not new table

-- For “don’t lose data even if someone deletes”, you don’t need a new table, just add a column:

ALTER TABLE students_master ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE student_marks ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE admission_details ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;


ALTER TABLE users
ADD COLUMN role_id INT REFERENCES roles(role_id);

-- Example roles table values
-- super_admin, admin, general

-- Manually assign roles to 2 specific users
UPDATE users
SET role_id = (SELECT role_id FROM roles WHERE role_name = 'super_admin')
WHERE email = 'shrutipnarule1410@gmail.com';

UPDATE users
SET role_id = (SELECT role_id FROM roles WHERE role_name = 'admin')
WHERE email = 'naruleshruti2004@gm;



ALTER TABLE users
ADD COLUMN failed_attempts INT DEFAULT 0,
ADD COLUMN lock_until TIMESTAMP NULL;

# Account Management & Role Handling Summary

## ✅ Current Implementation Status

### 1. Student Account Creation (Registration)
**File:** [routes/register_route.py](routes/register_route.py)

When a new account is created as a **STUDENT**:
- ✅ **users_master**: Creates entry with:
  - name, email, password, phone, role_id (= student), dob, address
  - Created with default role: **student**
  
- ✅ **students_master**: Creates entry with:
  - user_id (reference to users_master)
  - current_status = "active"

**Code Flow:**
```
1. Register form submitted
2. Validate email, password, name
3. Hash password
4. Get student role_id from roles_master
5. INSERT into users_master → Returns user_id
6. INSERT into students_master with user_id
7. COMMIT both operations
```

---

### 2. Role Change Management (NEW)
**File:** [routes/role_management.py](routes/role_management.py)
**Route:** `POST /change-role/<user_id>`

When changing a user's role:

#### Case 1: **PROMOTION** (student → admin/auditor/superadmin)
- ✅ **DELETE** from students_master (user is no longer a student)
- ✅ **UPDATE** users_master.role_id (new role assigned)
- ✅ Keep user in users_master with new role

```sql
-- DELETE from students_master
DELETE FROM students_master WHERE user_id = %s;

-- UPDATE role in users_master
UPDATE users_master SET role_id = %s WHERE id = %s;
```

#### Case 2: **DEMOTION** (admin/auditor/superadmin → student)
- ✅ **CREATE** new entry in students_master
- ✅ **UPDATE** users_master.role_id (set to student)
- ✅ Keep user in users_master with student role

```sql
-- CREATE new entry in students_master
INSERT INTO students_master (user_id, current_status) VALUES (%s, 'active');

-- UPDATE role in users_master
UPDATE users_master SET role_id = %s WHERE id = %s;
```

#### Case 3: **LATERAL CHANGE** (admin ↔ auditor ↔ superadmin)
- ✅ **UPDATE** users_master.role_id only
- ✅ No changes to students_master (user is not a student)

```sql
-- Only update role
UPDATE users_master SET role_id = %s WHERE id = %s;
```

---

### 3. Table Relationships

```
users_master (parent table)
├── id (primary key)
├── role_id (foreign key → roles_master)
├── name, email, password, phone, etc.
└── created_at, updated_at

students_master (child table)
├── id (primary key)
├── user_id (foreign key → users_master)
├── enrollment_no, current_status
└── created_at, updated_at

roles_master (lookup table)
├── id (primary key)
├── name ('student', 'admin', 'auditor', 'superadmin')
├── permissions (view_student, add_student, delete_student, etc.)
└── created_at, updated_at
```

---

### 4. Access Control

**Who can change roles?**
- ✅ Only **admin** or **superadmin** can change user roles
- ✅ Enforced via `@app.route()` method check in [routes/role_management.py](routes/role_management.py)

**Endpoint Protection:**
```python
if session.get("role") not in ["admin", "superadmin"]:
    abort(403)  # Forbidden
```

---

### 5. Usage Instructions

#### To Change a User's Role:
1. Go to `/change-role/<user_id>` (where user_id is the database ID)
2. Select the new role from dropdown
3. Review the action consequences
4. Submit the form

#### Example URLs:
- `/change-role/1` → Change user with ID 1's role
- `/change-role/42` → Change user with ID 42's role

---

### 6. Activity Logging

All role changes are logged in **activity_log** table:
- **Action:** ROLE_CHANGE
- **Entity:** USER
- **Metadata:** user_name, old_role, new_role
- **Timestamp:** auto-generated

---

## 📝 Schema Verification

### users_master structure:
```
id              TEXT PRIMARY KEY
name            TEXT
email           TEXT UNIQUE NOT NULL
password        TEXT NOT NULL
phone           VARCHAR(15)
role_id         TEXT REFERENCES roles_master(id)  ← Role is here
dob             DATE
address         TEXT
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### students_master structure:
```
id              TEXT PRIMARY KEY
user_id         TEXT REFERENCES users_master(id)  ← Link to user
enrollment_no   VARCHAR(30) UNIQUE
current_status  VARCHAR(20)
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### Key Point:
- A user in **students_master** is a STUDENT
- A user NOT in **students_master** but in **users_master** is admin/auditor/superadmin
- The actual role is defined by **users_master.role_id → roles_master**

---

## ✅ Tests to Verify Implementation

1. **Test Student Registration:**
   - Create new account
   - Verify entry in users_master with role_id = student
   - Verify entry in students_master with same user_id

2. **Test Promotion (Student → Admin):**
   - Use `/change-role/<student_user_id>`
   - Select "admin"
   - Verify:
     - users_master.role_id updated to admin
     - students_master entry DELETED for that user_id

3. **Test Demotion (Admin → Student):**
   - Use `/change-role/<admin_user_id>`
   - Select "student"
   - Verify:
     - users_master.role_id updated to student
     - students_master entry CREATED for that user_id

4. **Test Lateral Change (Admin → Auditor):**
   - Use `/change-role/<admin_user_id>`
   - Select "auditor"
   - Verify:
     - users_master.role_id updated to auditor
     - students_master unchanged (no entries)

---

## 🔧 Database Requirements

Ensure these sequences and tables exist:
```sql
CREATE SEQUENCE IF NOT EXISTS user_seq START 1;
CREATE SEQUENCE IF NOT EXISTS student_seq START 1;
CREATE SEQUENCE IF NOT EXISTS role_seq START 1;
CREATE SEQUENCE IF NOT EXISTS activity_seq START 1;

-- Ensure these roles exist:
INSERT INTO roles_master (name) VALUES ('student'), ('admin'), ('auditor'), ('superadmin');
```

---

## 📚 Files Modified/Created

✅ **Created:**
- [routes/role_management.py](routes/role_management.py) - Role change logic
- [templates/change_role.html](templates/change_role.html) - UI for role changes

✅ **Modified:**
- [routes/__init__.py](routes/__init__.py) - Added import for role_management
- [db.py](db.py) - Added load_dotenv() for proper environment setup

✅ **Verified:**
- [routes/register_route.py](routes/register_route.py) - Already implements correct dual-table insertion

---

## 📋 Summary

| Scenario | users_master | students_master | Action |
|----------|--------------|-----------------|--------|
| **New Student Registration** | ✅ INSERT with role_id=student | ✅ INSERT | Both tables |
| **Promote Student → Admin** | ✅ UPDATE role_id | ❌ DELETE | Remove from student table |
| **Demote Admin → Student** | ✅ UPDATE role_id | ✅ CREATE | Add to student table |
| **Change Admin → Auditor** | ✅ UPDATE role_id | — | Only update role |


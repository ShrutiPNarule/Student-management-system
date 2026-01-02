# ✅ 3-Level Approval Workflow - Complete Guide

## System Overview

The system now implements a **3-level data modification workflow** to ensure data quality and proper authorization:

```
┌──────────────────┐
│ Clerk/Admin      │
│ Submits Edit     │
└────────┬─────────┘
         ↓
    PENDING (Status)
         ↓
┌──────────────────────┐
│ AUDITOR Reviews      │
│ (Verify & Approve   │
│  or Reject)         │
└────────┬─────────────┘
         ↓
    AUDITOR_VERIFIED (Status)
    OR
    REJECTED_BY_AUDITOR
         ↓
┌──────────────────────┐
│ ADMIN Reviews        │
│ (Final Approve      │
│  or Reject)         │
└────────┬─────────────┘
         ↓
    ADMIN_APPROVED (Status)
    Data Applied to DB
    OR
    REJECTED_BY_ADMIN
```

---

## Component Details

### 1️⃣ Database Layer (`db.py`)

**Table: `pending_changes`**
```sql
CREATE TABLE pending_changes (
    id TEXT PRIMARY KEY (PC000001, PC000002, ...),
    change_type TEXT,              -- 'edit_student', 'add_student'
    student_id TEXT,               -- NULL for new students, ID for edits
    data JSONB,                    -- New/modified data
    original_data JSONB,           -- Original data for comparison
    created_by TEXT,               -- Clerk/Admin who initiated
    created_at TIMESTAMP,
    status TEXT,                   -- pending, auditor_verified, etc.
    auditor_id TEXT,               -- Auditor who verified
    auditor_verified_at TIMESTAMP,
    auditor_remarks TEXT,
    admin_id TEXT,                 -- Admin who approved
    admin_approved_at TIMESTAMP,
    admin_remarks TEXT,
    updated_at TIMESTAMP
);
```

**Status Values:**
- `pending` - Waiting for auditor review
- `auditor_verified` - Auditor approved, waiting for admin
- `rejected_by_auditor` - Auditor rejected
- `admin_approved` - Admin approved and applied to DB
- `rejected_by_admin` - Admin rejected

---

### 2️⃣ Clerk/Admin Submission (`routes/edit_route.py`)

**What Happens:**
1. Clerk or Admin fills out edit form
2. Data is validated
3. Change is stored in `pending_changes` table with:
   - `status = 'pending'`
   - `data` = new values (JSONB)
   - `original_data` = current values (JSONB)
   - `created_by` = user who submitted

**User Message:** "Edit request sent to auditor for verification and admin for approval."

---

### 3️⃣ Auditor Verification (`routes/auditor_verification.py`)

**Route:** `/auditor/pending-changes`
**Menu Link:** Dashboard → Profile → ✅ Verify Changes

**What Auditor Sees:**
- List of all pending changes
- Side-by-side comparison (proposed vs. original)
- Option to verify (approve) or reject

**When Auditor Approves:**
- Status changes to `auditor_verified`
- `auditor_id`, `auditor_verified_at`, `auditor_remarks` are populated
- Request moves to Admin's approval queue

**When Auditor Rejects:**
- Status changes to `rejected_by_auditor`
- Clerk is notified to resubmit if needed

---

### 4️⃣ Admin Final Approval (`routes/admin_approval_workflow.py`)

**Route:** `/admin/pending-approvals`
**Menu Link:** Dashboard → Profile → ✅ Verify Changes (Auditor Approved)

**What Admin Sees:**
- List of auditor-verified changes only
- Auditor's remarks and reasoning
- Side-by-side comparison
- Option to approve (apply) or reject

**When Admin Approves:**
- Status changes to `admin_approved`
- Data is applied to main database:
  - `users_master` is updated
  - `students_master` is updated
  - `student_marks` is updated
- `admin_id`, `admin_approved_at`, `admin_remarks` are populated

**When Admin Rejects:**
- Status changes to `rejected_by_admin`
- Data is NOT applied
- Original data remains unchanged

---

## Testing the Workflow

### Step 1: Create Test Data
1. Login as **Clerk**
2. Go to Home → Search or Add Student
3. Edit a student record
4. Fill in form and submit
5. You should see: "Edit request sent to auditor for verification and admin for approval."

### Step 2: Auditor Review
1. Logout from Clerk
2. Login as **Auditor**
3. Click Profile (👤) → **✅ Verify Changes**
4. You should see the pending edit
5. Review the proposed changes (green) vs. original (yellow strikethrough)
6. Add optional remarks
7. Click **✅ Verify & Approve** OR **❌ Reject Change**

### Step 3: Admin Final Approval
1. Logout from Auditor
2. Login as **Admin**
3. Click Profile (👤) → **✅ Verify Changes (Auditor Approved)**
4. You should see the auditor-verified edit
5. Review auditor's remarks
6. Add admin remarks (optional)
7. Click **✅ Approve & Apply to System** OR **❌ Reject Change**
8. If approved, check if data was updated in main DB

### Step 4: Verify Success
1. Go back to search/view that student
2. Confirm the edited data is present if admin approved
3. Confirm original data if admin rejected

---

## Troubleshooting

### Issue: "Requests not showing in Admin approvals"

**Check:**
1. Auditor must have APPROVED (not rejected) the change
2. Status must be `auditor_verified` in database
3. Query: `SELECT * FROM pending_changes WHERE status = 'auditor_verified';`
4. Verify `auditor_id` is NOT NULL

### Issue: "Data not applied after admin approval"

**Check:**
1. Status changed to `admin_approved` (query: `SELECT status FROM pending_changes WHERE id = 'PCXXXXXX';`)
2. Check if user exists in `users_master` and `students_master`
3. Look at error logs in Flask console
4. Verify email is not already taken by another user

### Issue: "Can't see verification page (404 error)"

**Check:**
1. Route imports are added in `routes/__init__.py`
2. Verify: `from .auditor_verification import *`
3. Verify: `from .admin_approval_workflow import *`
4. Restart Flask server

---

## Menu Navigation

### Clerk
- Dashboard → Profile (👤)
- Can see their edit requests in approval timeline

### Auditor
- Dashboard → Profile (👤) → **✅ Verify Changes**
- Can view all pending changes
- Can approve/reject with remarks

### Admin
- Dashboard → Profile (👤) → **✅ Verify Changes (Auditor Approved)**
- Can view auditor-verified changes only
- Can approve (applies to DB) or reject

---

## Database Queries for Verification

### All Pending Changes
```sql
SELECT id, change_type, status, created_by, created_at 
FROM pending_changes 
WHERE status IN ('pending', 'auditor_verified', 'admin_approved');
```

### Changes Auditor Should See
```sql
SELECT * FROM pending_changes WHERE status = 'pending';
```

### Changes Admin Should See
```sql
SELECT * FROM pending_changes WHERE status = 'auditor_verified';
```

### Completed/Applied Changes
```sql
SELECT * FROM pending_changes WHERE status = 'admin_approved';
```

---

## Key Files

| File | Purpose |
|------|---------|
| `db.py` | Creates `pending_changes` table |
| `routes/edit_route.py` | Creates pending change on submission |
| `routes/auditor_verification.py` | Auditor review & approval |
| `routes/admin_approval_workflow.py` | Admin final approval & application |
| `templates/auditor_verify_changes.html` | Auditor UI |
| `templates/admin_approve_changes.html` | Admin UI |
| `templates/base.html` | Menu links |

---

## Success Indicators

✅ System is working correctly if:
1. Edit submitted → appears in auditor's pending list
2. Auditor approves → disappears from auditor's list
3. Change appears in admin's approval list
4. Admin approves → status becomes `admin_approved`
5. Data is applied to database (visible in search/view)
6. Complete audit trail with timestamps and remarks

---

**Last Updated:** January 2, 2026

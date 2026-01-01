# Data Verification & Approval Workflow

## Overview
This document describes the new three-step approval workflow for data additions and edits in the system.

## Workflow Process

### Step 1️⃣ Data Entry (Admin/Clerk)
- Admin or Clerk submits a new student record or edit
- Data is **NOT** directly saved to the main database
- Data is stored in the `pending_changes` table with status = **'pending'**
- The change includes:
  - Change type (add_student, edit_student)
  - Complete data (JSONB format)
  - Original data (for edits, for comparison)
  - Submitted by user ID and timestamp

### Step 2️⃣ Auditor Verification
- **Auditor** accesses `/auditor/pending-changes`
- Reviews all pending changes with side-by-side comparison:
  - Proposed new data
  - Original data (highlighted as deleted)
- Auditor can:
  - ✅ **Verify & Approve** - Sends to admin for final approval
  - ❌ **Reject** - Rejects the change with remarks

**Change Status:** pending → **auditor_verified** OR **rejected_by_auditor**

### Step 3️⃣ Admin Final Approval
- **Admin** accesses `/admin/pending-approvals`
- Reviews changes already verified by auditor
- Sees auditor's remarks and reasoning
- Admin can:
  - ✅ **Approve & Apply** - Change is applied to main database
  - ❌ **Reject** - Rejects with admin remarks

**Change Status:** auditor_verified → **admin_approved** (applied) OR **rejected_by_admin**

## Data Flow

```
┌─────────────────────┐
│   Admin/Clerk       │
│   Submits Data      │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │   PENDING    │  (pending_changes table)
    │  Status: 0   │
    └──────┬───────┘
           │
           ▼ (Auditor Review)
    ┌──────────────────────────────┐
    │  Auditor Verifies & Remarks  │
    └──────┬───────────────────────┘
           │
    ┌──────┴────────┐
    │               │
    ▼               ▼
VERIFIED       REJECTED
(Auditor)      (Auditor)
    │               │
    ▼               │
┌──────────────┐    │
│  AUDITOR     │    │
│  VERIFIED    │    │
│  Status: 1   │    │
└──────┬───────┘    │
       │            │
       ▼ (Admin Review)
    ┌──────────────────────────────┐
    │  Admin Approves/Rejects      │
    └──────┬───────────────────────┘
           │
    ┌──────┴────────┐
    │               │
    ▼               ▼
APPROVED       REJECTED
(Admin)        (Admin)
    │               │
    ▼               │
┌────────────────┐  │
│  APPLIED TO    │  │
│  MAIN DB       │  │
│  Status: 2     │  │
└────────────────┘  │
                    │
                    ▼
              ❌ NOT APPLIED
              (Removed from home)
```

## Database Tables

### pending_changes Table
```sql
CREATE TABLE pending_changes (
    id TEXT PRIMARY KEY (PC000001, PC000002, ...),
    change_type TEXT,         -- 'add_student', 'edit_student'
    student_id TEXT,          -- NULL for new adds, ID for edits
    
    data JSONB,               -- Complete new/modified data
    original_data JSONB,      -- Original data (for edits)
    
    created_by TEXT,          -- User who initiated change
    created_at TIMESTAMP,
    
    status TEXT,              -- See statuses below
    
    auditor_id TEXT,          -- Auditor who verified
    auditor_verified_at TIMESTAMP,
    auditor_remarks TEXT,
    
    admin_id TEXT,            -- Admin who approved/rejected
    admin_approved_at TIMESTAMP,
    admin_remarks TEXT,
    
    updated_at TIMESTAMP
);
```

### Change Status Values
- **pending** - Waiting for auditor verification
- **auditor_verified** - Auditor approved, awaiting admin
- **rejected_by_auditor** - Auditor rejected the change
- **admin_approved** - Admin approved and applied
- **rejected_by_admin** - Admin rejected the change
- **completed** - Successfully applied to main system

## Routes

### For Auditor
- **GET `/auditor/pending-changes`** - View all pending changes
- **POST `/auditor/verify-change/<change_id>`** - Verify or reject a change

### For Admin
- **GET `/admin/pending-approvals`** - View auditor-verified changes
- **POST `/admin/approve-change/<change_id>`** - Approve or reject a change

## Key Features

✅ **Two-Level Verification**
- Auditor ensures data quality
- Admin ensures business logic

✅ **Complete Audit Trail**
- Every change is logged
- Timestamps for each step
- Remarks from both auditor and admin

✅ **Data Backup**
- Original data preserved for comparison
- Easy rollback if needed

✅ **Transparency**
- Changes visible to both auditor and admin
- Side-by-side comparison of old vs new

✅ **Role-Based Access**
- Only auditor can verify
- Only admin can apply
- No bypassing the workflow

## Implementation Notes

1. **Modify add_route.py** to store data in pending_changes instead of directly
2. **Modify edit_route.py** to store edits in pending_changes instead of directly
3. **Import new routes** in app.py
4. **Home page** should only display approved data (status = 'admin_approved' and applied)

## Future Enhancements

- Email notifications at each stage
- Dashboard widgets showing pending count
- Approval workflow statistics/reports
- Bulk approval for similar changes
- Change history for each student

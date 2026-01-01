# 📋 Data Verification Workflow - Quick Reference

## System Overview

When data is **added or edited**, it must pass through a 3-stage approval process:

```
STEP 1: DATA ENTRY
  • Admin/Clerk submits student data
  • Data stored in pending_changes table
  • Status: 'pending'
  
        ↓
        
STEP 2: AUDITOR VERIFICATION
  • Auditor reviews proposed data
  • Compares with original data
  • Approves or rejects with remarks
  • Status: 'auditor_verified' OR 'rejected_by_auditor'
  
        ↓
        
STEP 3: ADMIN FINAL APPROVAL
  • Admin reviews auditor's decision
  • Reviews auditor's remarks
  • Approves (applies to DB) or rejects
  • Status: 'admin_approved' (applied) OR 'rejected_by_admin'
  
        ↓
        
DONE: DATA UPDATED
  • Only approved data appears on home screen
  • Complete audit trail maintained
```

---

## Role Permissions

### 👨‍💼 ADMIN / CLERK
- ✅ Submit new student data
- ✅ Submit edits to student data
- ✅ Access `/admin/pending-approvals` (admin only)
- ❌ Cannot directly update database
- ❌ Cannot skip auditor verification

### 🔍 AUDITOR
- ✅ Access `/auditor/pending-changes`
- ✅ View all pending changes with side-by-side comparison
- ✅ Approve changes (forward to admin)
- ✅ Reject changes with remarks
- ✅ View activity logs
- ❌ Cannot directly apply changes to database

### 👨‍💻 SUPERADMIN
- ✅ Change user roles
- ✅ Approve applications
- ✅ View activity logs
- ❌ Not involved in data approval workflow

---

## Accessing the Workflow

### For Auditor
1. Login with auditor account
2. Go to **Auditor Dashboard**
3. Click **"Pending Changes"** or visit `/auditor/pending-changes`
4. Review each change with proposed vs original data
5. Click **"Verify & Approve"** or **"Reject Change"**
6. Add remarks if needed
7. Submit decision

### For Admin
1. Login with admin account
2. Go to **Admin Dashboard**
3. Click **"Pending Approvals"** or visit `/admin/pending-approvals`
4. See changes already verified by auditor
5. Review auditor's remarks
6. Click **"Approve & Apply to System"** or **"Reject Change"**
7. Add remarks if needed
8. Submit decision

---

## Change Status Reference

| Status | Where | What It Means |
|--------|-------|---------------|
| **pending** | Pending Changes (Auditor View) | Waiting for auditor review |
| **auditor_verified** | Pending Approvals (Admin View) | Auditor approved, waiting for admin |
| **rejected_by_auditor** | Rejected List | Auditor rejected (will be re-submitted) |
| **admin_approved** | Completed Changes | Admin approved and applied to DB |
| **rejected_by_admin** | Rejected List | Admin rejected (will be re-submitted) |
| **completed** | History | Successfully applied to system |

---

## Data Comparison Screen

### What You See as Auditor:
```
┌─────────────────────────────────────────────────────────┐
│  CHANGE #PC000001 - ADD_STUDENT                         │
│  By: Shruti | 15 Jan 2026, 10:30 AM                    │
│                                                         │
│  PROPOSED CHANGES        │  ORIGINAL DATA (if edit)    │
│  ├─ Name: John Doe       │  ├─ Name: ~~Jane Doe~~     │
│  ├─ Email: john@...      │  ├─ Email: ~~jane@...~~    │
│  ├─ Phone: 9876543210    │  ├─ Phone: ~~9876543210~~ │
│  ├─ Marks 10th: 85       │  ├─ Marks 10th: ~~80~~    │
│  └─ ...                  │  └─ ...                     │
│                                                         │
│  [Verify & Approve]  [Reject Change]                   │
│  Remarks: [__________________________________]         │
└─────────────────────────────────────────────────────────┘
```

---

## Database Flow

```
Data Submission
    ↓
pending_changes table
    ├─ change_type: 'add_student'
    ├─ data: {name, email, phone, marks, ...}
    ├─ status: 'pending'
    └─ created_by: admin_id, created_at: now
    ↓
Auditor Review (check_permissions.py)
    ├─ Verify data quality
    ├─ Check for duplicates
    ├─ Update: auditor_id, auditor_verified_at, status
    └─ Add: auditor_remarks
    ↓
Admin Approval (admin_approval_workflow.py)
    ├─ Review auditor's decision
    ├─ Apply change to actual tables:
    │  ├─ INSERT INTO users_master (...)
    │  ├─ INSERT INTO students_master (...)
    │  └─ INSERT INTO student_marks (...)
    ├─ Update: admin_id, admin_approved_at, status
    └─ Add: admin_remarks
    ↓
Home Screen Display
    └─ Only shows students from approved changes
```

---

## Key Features

✅ **Two-level Quality Check**
- Auditor catches data quality issues
- Admin ensures business logic is followed

✅ **Complete Transparency**
- See all remarks from both reviewers
- Know why things were approved/rejected

✅ **Data Integrity**
- Original data always preserved
- No direct database updates allowed
- Easy to audit and trace

✅ **Audit Trail**
- Who submitted the data
- When it was reviewed
- What remarks were made
- Complete history preserved

---

## Common Scenarios

### ✅ Scenario 1: Clean Data Path
```
Admin submits data
  ↓
Auditor: "Data looks good!" → Approve
  ↓
Admin: "Approved by auditor, apply it" → Approve
  ↓
Data appears on home screen ✅
```

### ❌ Scenario 2: Data Quality Issue
```
Admin submits data
  ↓
Auditor: "Phone number invalid!" → Reject
  ↓
Admin: Informed of rejection
  ↓
Admin resubmits with correct phone
  ↓
Auditor: "Now it's correct!" → Approve
  ↓
Admin: Approves
  ↓
Data appears on home screen ✅
```

### ⚠️ Scenario 3: Admin Override
```
Admin submits data
  ↓
Auditor: "Unusual marks for this student" → Approve anyway
  ↓
Admin: "I authorized these marks" → Approve
  ↓
Data appears on home screen with remarks
```

---

## Tips & Best Practices

🎯 **For Auditor:**
- Always add remarks when rejecting
- Compare with existing student data for consistency
- Check phone, email, and marks for validity

🎯 **For Admin:**
- Review auditor's remarks carefully
- Don't approve if you disagree
- Add remarks for any rejections

🎯 **For Data Quality:**
- Fill all required fields
- Double-check phone numbers and emails
- Ensure marks are within valid ranges
- Avoid duplicate records

---

## Troubleshooting

**Q: Why can't I add students directly?**
A: All data goes through the verification workflow for quality control.

**Q: How long does approval take?**
A: It depends on auditor and admin availability. Usually same day for most organizations.

**Q: Can I cancel a pending change?**
A: Currently, changes can only be rejected. Contact the admin to resubmit.

**Q: What if auditor approves but admin rejects?**
A: The change is rejected and can be resubmitted with corrections.

**Q: Can students see pending changes?**
A: No, only auditor and admin can see pending changes.

---

## System Admin Notes

- **Table:** `pending_changes` stores all workflow data
- **Sequences:** `pending_change_seq` generates unique IDs
- **Indices:** Created on status, created_by, student_id, auditor_id, admin_id
- **Default Status:** 'pending' (waiting for auditor)

---

**Last Updated:** January 1, 2026
**Status:** ✅ Fully Implemented and Ready to Use

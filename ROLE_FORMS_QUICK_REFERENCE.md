# 📋 ROLE-BASED FORMS ACCESS - QUICK REFERENCE CARD

## At a Glance

```
┌────────────────────────────────────────────────────────────────────────┐
│                     FORMS ACCESS BY ROLE                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  👑 SUPERADMIN (45 FORMS)                                             │
│  ├─ ✅ View everything                                               │
│  ├─ ❌ Cannot add/edit students directly                            │
│  ├─ ✅ Change user roles                                            │
│  ├─ ✅ Approve applications                                         │
│  ├─ ✅ Session management                                           │
│  ├─ ✅ Security configuration                                       │
│  └─ 📌 Oversight role only                                          │
│                                                                        │
│  👨‍💼 ADMIN (45 FORMS)                                                  │
│  ├─ ✅ Submit student data (via approval workflow)                  │
│  ├─ ✅ Approve auditor-verified changes                             │
│  ├─ ✅ Add marks & attendance                                       │
│  ├─ ✅ Bulk upload & approval                                       │
│  ├─ ✅ User & account management                                    │
│  ├─ ✅ View all reports                                             │
│  ❌ Cannot change roles                                              │
│  └─ 📌 Day-to-day operations                                        │
│                                                                        │
│  📋 CLERK (27 FORMS)                                                  │
│  ├─ ✅ Submit student data (via approval)                           │
│  ├─ ✅ Add marks & attendance                                       │
│  ├─ ✅ Manage documents & scholarships                              │
│  ├─ ✅ View reports                                                 │
│  ├─ ✅ Restore deleted students                                     │
│  ❌ Cannot approve anything                                           │
│  ❌ Cannot access admin functions                                    │
│  └─ 📌 Support & data entry                                         │
│                                                                        │
│  🔍 AUDITOR (22 FORMS)                                                │
│  ├─ ✅ View pending changes                                         │
│  ├─ ✅ Verify/reject data quality                                   │
│  ├─ ✅ View student data                                            │
│  ├─ ✅ View reports & logs                                          │
│  ❌ Cannot add/edit/delete students                                  │
│  ❌ Cannot apply changes                                             │
│  ❌ Cannot access admin functions                                    │
│  └─ 📌 Quality control only                                         │
│                                                                        │
│  👨‍🎓 STUDENT (10 FORMS)                                               │
│  ├─ ✅ Login & register                                             │
│  ├─ ✅ Change password & 2FA                                        │
│  ├─ ✅ Mark attendance                                              │
│  ├─ ✅ Upload documents                                             │
│  ✅ Apply for scholarships                                           │
│  ❌ Cannot view other students                                       │
│  ❌ Cannot access any admin functions                                │
│  └─ 📌 Self-service only                                            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Form Categories & Access

### 🔐 AUTHENTICATION (8 Forms)
Everyone can access these (except Student cannot register with admin account)

| Form | Public | Student | Auditor | Clerk | Admin | Superadmin |
|------|--------|---------|---------|-------|-------|------------|
| Login | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Register | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Forgot Password | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reset Password | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2FA Setup | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OTP Verify | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Change Password | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete Account | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 👥 STUDENT DATA ENTRY (7 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Add Student | ❌ | ❌ | ⏳ Pending | ⏳ Pending | ❌ |
| Edit Student | ❌ | ❌ | ⏳ Pending | ⏳ Pending | ❌ |
| Delete Student | ❌ | ❌ | ⏳ Pending | ⏳ Pending | ❌ |
| View Students | ❌ | ✅ | ✅ | ✅ | ✅ |
| Bulk Upload | ❌ | ❌ | ✅ | ✅ | ❌ |
| Bulk Approval | ❌ | ❌ | ❌ | ✅ | ❌ |
| View Profile | ❌ | ✅ | ✅ | ✅ | ✅ |

### 📊 MARKS & ATTENDANCE (3 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Update Marks | ❌ | ❌ | ✅ | ✅ | ❌ |
| Attendance | ✅ | ❌ | ✅ | ✅ | ❌ |
| Attendance Report | ❌ | ✅ | ✅ | ✅ | ✅ |

### 📝 DOCUMENTS & SCHOLARSHIP (3 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Scholarship | ✅ | ❌ | ✅ | ✅ | ❌ |
| Upload Docs | ✅ | ❌ | ✅ | ✅ | ❌ |
| View Docs | ❌ | ✅ | ✅ | ✅ | ✅ |

### 📋 DATA VERIFICATION & APPROVAL (5 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Submit Data | ❌ | ❌ | ✅ | ✅ | ❌ |
| Verify Changes | ❌ | ✅ | ❌ | ❌ | ❌ |
| Approve Changes | ❌ | ❌ | ❌ | ✅ | ❌ |
| Approvals | ❌ | ❌ | ❌ | ✅ | ✅ |
| Approval Dashboard | ❌ | ❌ | ❌ | ✅ | ✅ |

### 🔄 RECYCLE BIN (2 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| View Recycle Bin | ❌ | ✅ | ✅ | ✅ | ✅ |
| Restore Student | ❌ | ❌ | ✅ | ✅ | ❌ |

### 👤 ROLE & USER MANAGEMENT (5 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Change Role | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage Roles | ❌ | ❌ | ❌ | ❌ | ✅ |
| User Management | ❌ | ❌ | ❌ | ✅ | ✅ |
| Permission Assign | ❌ | ❌ | ❌ | ✅ | ✅ |
| Edit Permissions | ❌ | ❌ | ❌ | ✅ | ✅ |

### 🔐 ACCOUNT MANAGEMENT (5 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Account Activation | ❌ | ❌ | ❌ | ✅ | ✅ |
| Account Deletion | ❌ | ❌ | ❌ | ✅ | ✅ |
| IP Management | ❌ | ❌ | ❌ | ✅ | ✅ |
| Session Management | ❌ | ❌ | ❌ | ❌ | ✅ |
| Security Config | ❌ | ❌ | ❌ | ✅ | ✅ |

### 📊 REPORTS & ANALYTICS (4 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Academic Report | ❌ | ✅ | ✅ | ✅ | ✅ |
| College Report | ❌ | ✅ | ✅ | ✅ | ✅ |
| Attendance Report | ❌ | ✅ | ✅ | ✅ | ✅ |
| Category Stats | ❌ | ✅ | ✅ | ✅ | ✅ |

### 📝 LOGS & AUDIT (4 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| Activity Logs | ❌ | ✅ | ✅ | ✅ | ✅ |
| Audit Logs | ❌ | ❌ | ❌ | ✅ | ✅ |
| Approval Audit | ❌ | ❌ | ❌ | ✅ | ✅ |
| View Logs | ❌ | ❌ | ❌ | ✅ | ✅ |

### 🔧 SYSTEM MANAGEMENT (2 Forms)

| Form | Student | Auditor | Clerk | Admin | Superadmin |
|------|---------|---------|-------|-------|------------|
| System Health | ❌ | ❌ | ❌ | ✅ | ✅ |
| Notifications | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Common Questions

### "Can I add a student?"
- ✅ **Admin** - Yes, via submission (goes to auditor)
- ✅ **Clerk** - Yes, via submission (goes to auditor)
- ❌ **Superadmin** - No (oversight only)
- ❌ **Auditor** - No (verification only)
- ❌ **Student** - No

### "Can I approve something?"
- ✅ **Admin** - Yes (after auditor verifies)
- ✅ **Superadmin** - Yes (applications & approvals)
- ❌ **Clerk** - No (cannot approve)
- ❌ **Auditor** - No (can only verify)
- ❌ **Student** - No

### "Can I verify data?"
- ✅ **Auditor** - Yes (only role that can)
- ❌ **Admin** - No (can only approve)
- ❌ **Clerk** - No
- ❌ **Superadmin** - No
- ❌ **Student** - No

### "Can I change someone's role?"
- ✅ **Superadmin** - Yes (only one who can)
- ❌ **Admin** - No
- ❌ **Clerk** - No
- ❌ **Auditor** - No
- ❌ **Student** - No

### "Can I view all reports?"
- ✅ **Superadmin** - Yes
- ✅ **Admin** - Yes
- ✅ **Clerk** - Yes
- ✅ **Auditor** - Yes
- ❌ **Student** - No

### "Can I delete a student?"
- ✅ **Admin** - Yes (via submission)
- ✅ **Clerk** - Yes (via submission)
- ❌ **Superadmin** - No (oversight only)
- ❌ **Auditor** - No
- ❌ **Student** - No

---

## Form Access by Workflow

### Data Entry Workflow
```
Admin/Clerk submits data (Add/Edit/Delete)
        ↓
Data stored as PENDING
        ↓
Auditor verifies quality
        ├─ Approves → auditor_verified
        └─ Rejects → rejected_by_auditor
        ↓
Admin reviews & applies
        ├─ Approves → admin_approved (appears on home screen)
        └─ Rejects → rejected_by_admin
```

### Who Does What
- **Submit:** Admin, Clerk
- **Verify:** Auditor
- **Approve:** Admin
- **View:** Everyone (except Student)

---

## Access Hierarchy

```
Highest Privilege
       ↑
       │ 👑 SUPERADMIN (45 forms)
       │ • Oversight roles
       │ • Critical decisions
       │
       ├─ 👨‍💼 ADMIN (45 forms)
       │  • Operations & data
       │  • Approvals
       │
       ├─ 📋 CLERK (27 forms)
       │  • Data entry & support
       │  • Limited approval
       │
       ├─ 🔍 AUDITOR (22 forms)
       │  • Verification only
       │  • Quality control
       │
       └─ 👨‍🎓 STUDENT (10 forms)
          • Self-service
          • Personal account
       ↓
Lowest Privilege
```

---

## Summary Table

| Role | Total Forms | Submit | Verify | Approve | Admin | View |
|------|------------|--------|--------|---------|-------|------|
| **Superadmin** | 45 | ❌ 0 | ❌ 0 | ✅ 7 | ✅ 23 | ✅ 15 |
| **Admin** | 45 | ✅ 15 | ❌ 0 | ✅ 7 | ✅ 8 | ✅ 15 |
| **Clerk** | 27 | ✅ 12 | ❌ 0 | ❌ 0 | ✅ 6 | ✅ 9 |
| **Auditor** | 22 | ❌ 0 | ✅ 3 | ❌ 0 | ❌ 0 | ✅ 19 |
| **Student** | 10 | ✅ 2 | ❌ 0 | ❌ 0 | ❌ 0 | ✅ 8 |

---

**Total System Forms: 68**
**Last Updated: January 1, 2026**
**Status: ✅ Complete & Current**

================================================================================
📊 ALL ROLES WITH PERMISSIONS
================================================================================

Role            View   Add    Delete   ChgRole  Marks  Log    Create   Approve
--------------------------------------------------------------------------------
admin           ✅      ❌      ❌        ❌        ❌      ✅      ❌        ✅
auditor         ✅      ❌      ❌        ❌        ❌      ✅      ❌        ❌
clerk           ✅      ✅      ✅        ❌        ✅      ✅      ❌        ❌
student         ❌      ❌      ❌        ❌        ❌      ❌      ❌        ❌
superadmin      ❌      ❌      ❌        ✅        ❌      ✅      ❌        ✅
================================================================================

## Column Definitions

| Column | Description |
|--------|-------------|
| **View** | Can view student data |
| **Add** | Can add new students |
| **Delete** | Can delete students |
| **ChgRole** | Can change user roles |
| **Marks** | Can add marks & attendance |
| **Log** | Can view activity logs |
| **Create** | Can create applications/documents |
| **Approve** | Can approve data & applications |

## Role Summary

### 👨‍💼 ADMIN
- ✅ View (Reports/Analysis), Log (Activity), Approve (Data)
- ❌ Add, Delete, Marks, Change Role, Create
- **Role:** Review & approval authority only, no data entry

### 🔍 AUDITOR
- ✅ View, Log
- ❌ Add, Delete, Change Role, Marks, Create, Approve
- **Role:** Data verification & quality control only

### 📋 CLERK
- ✅ View, Add, Delete, Marks, Log
- ❌ Change Role, Create, Approve
- **Role:** Data entry support, no approval authority

### 👨‍🎓 STUDENT
- ❌ All permissions blocked at admin level
- **Role:** Self-service access only (register, change password, apply scholarships)

### 👑 SUPERADMIN
- ✅ Change Role, Log, Approve
- ❌ View, Add, Delete, Marks, Create
- **Role:** System oversight, critical decisions, limited access

---

## Permission Statistics

| Role | Total Permissions | Percentage |
|------|-------------------|-----------|
| Admin | 3/8 | 37.5% |
| Clerk | 5/8 | 62.5% |
| Superadmin | 3/8 | 37.5% |
| Auditor | 2/8 | 25% |
| Student | 0/8 | 0% |

---

## Key Rules

✅ **CAN:** Admin can view reports and analysis
✅ **CAN:** Admin can approve changes after auditor verification
✅ **CAN:** Admin can view activity logs
✅ **CAN:** Clerk can add marks and students (via approval)
✅ **CAN:** Auditor can view everything but NOT modify
✅ **CAN:** Superadmin can change roles and approve applications
✅ **CAN:** Student can manage own account only

❌ **CANNOT:** Admin add/edit/delete students (approval only)
❌ **CANNOT:** Superadmin add/edit/delete students directly
❌ **CANNOT:** Clerk approve anything
❌ **CANNOT:** Auditor make any changes
❌ **CANNOT:** Student access admin features
❌ **CANNOT:** Anyone bypass approval workflow for student data

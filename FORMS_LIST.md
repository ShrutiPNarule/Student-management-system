# 📋 Forms in Student Management System

## Total Forms: **50 Comprehensive Forms**

---

## 🔐 **AUTHENTICATION & LOGIN FORMS** (8 Forms)

### **1. Login Form** 
- **File**: [login.html](login.html)
- **Purpose**: User authentication with email & password
- **Fields**: Email, Password, Remember Me checkbox, CSRF Token
- **Method**: POST
- **Route**: `/login`
- **Access**: Public

---

### **2. Register Form**
- **File**: [register.html](register.html)
- **Purpose**: New user account creation
- **Fields**: Name, Email, Password, Confirm Password, Phone, Address/College
- **Method**: POST
- **Route**: `/register`
- **Access**: Public
- **Validation**: Email uniqueness, Password strength, Phone format

---

### **3. OTP Verification Form**
- **File**: [verify_otp.html](verify_otp.html)
- **Purpose**: Verify OTP during login & registration
- **Fields**: OTP Code (6 digits), Resend OTP link, Remember Me checkbox
- **Method**: POST
- **Route**: `/verify-otp`
- **Access**: Logged-in users
- **Expiry**: 10 minutes

---

### **4. Resend OTP Form**
- **File**: [verify_otp.html](verify_otp.html)
- **Purpose**: Request new OTP when previous expires
- **Fields**: Email (hidden), OTP resend button
- **Method**: POST
- **Route**: `/resend-otp`
- **Access**: During OTP verification
- **Rate Limit**: Max 3 resends per session

---

### **5. Forgot Password Form**
- **File**: [forgot_password.html](forgot_password.html)
- **Purpose**: Request password reset link via email
- **Fields**: Email, CSRF Token
- **Method**: POST
- **Route**: `/forgot-password`
- **Access**: Public
- **Output**: Confirmation message

---

### **6. Reset Password Form**
- **File**: [reset_password.html](reset_password.html)
- **Purpose**: Set new password using reset token
- **Fields**: New Password, Confirm Password, CSRF Token
- **Method**: POST
- **Route**: `/reset-password/<token>`
- **Access**: Email link
- **Validation**: Password strength, Token expiry (24 hours)

---

### **7. Change Password Form** *(New)*
- **File**: [change_password.html](change_password.html) *(To be created)*
- **Purpose**: Authenticated user changes their password
- **Fields**: Current Password, New Password, Confirm Password
- **Method**: POST
- **Route**: `/change-password`
- **Access**: Authenticated users (all roles)
- **Validation**: Current password verification, Password strength

---

### **8. Two-Factor Authentication Setup Form** *(New)*
- **File**: [2fa_setup.html](2fa_setup.html) *(To be created)*
- **Purpose**: Enable 2FA for account security
- **Fields**: QR Code, Secret Key, Backup Codes, Verification Code
- **Method**: POST
- **Route**: `/2fa/setup`
- **Access**: Authenticated users
- **Optional**: Can be skipped

---

## 👥 **STUDENT MANAGEMENT FORMS** (12 Forms)

### **9. Add Student Form**
- **File**: [add_student.html](add_student.html)
- **Purpose**: Admin adds new student record
- **Fields**: 
  - Name, Roll Number, College
  - Phone, Email, Date of Birth
  - Birth Place, Religion, Category, Caste
  - Marks (10th, 12th, Year 1-4)
  - Semester Details, GPA
- **Method**: POST
- **Route**: `/add`
- **Role Required**: Admin
- **Validation**: Email uniqueness, Phone format, DOB age check

---

### **10. Edit Student Form**
- **File**: [edit_student.html](edit_student.html)
- **Purpose**: Admin requests to edit student data
- **Fields**: Same as Add Student (all student fields)
- **Method**: POST
- **Route**: `/edit/<student_id>`
- **Role Required**: Admin
- **Approval**: Requires superadmin approval
- **Audit**: Logs all changes

---

### **11. Bulk Upload Student Form** *(New)*
- **File**: [bulk_upload_students.html](bulk_upload_students.html) *(To be created)*
- **Purpose**: Admin uploads multiple student records via CSV
- **Fields**: CSV File upload, Encoding selection, Sample template download
- **Method**: POST (multipart/form-data)
- **Route**: `/bulk-upload-students`
- **Role Required**: Admin
- **Validation**: CSV format, Duplicate detection, Error logging

---

### **12. Student Search & Filter Form** *(New)*
- **File**: [search_students.html](search_students.html) *(To be created)*
- **Purpose**: Search students by multiple criteria
- **Fields**: 
  - Search by: Name, Roll Number, Email, Phone
  - Filter by: College, Category, Year, GPA range
  - Sort by: Name, Roll Number, GPA
- **Method**: GET/POST
- **Route**: `/search-students`
- **Role Required**: Admin, Auditor
- **Features**: Export results to CSV

---

### **13. Student Profile View Form** *(New)*
- **File**: [student_profile.html](student_profile.html) *(To be created)*
- **Purpose**: View complete student profile with history
- **Fields**: All student data (read-only), Academic history, Approval requests
- **Method**: GET
- **Route**: `/student/<student_id>/profile`
- **Role Required**: Admin, Auditor, Superadmin
- **Displays**: Student details, Edit history, Approval timeline

---

### **14. Delete Student Request Form**
- **File**: [index.html](index.html) (inline form)
- **Purpose**: Admin requests to delete student record
- **Fields**: Reason for deletion (textarea), Confirmation checkbox
- **Method**: POST
- **Route**: `/delete/<student_id>`
- **Role Required**: Admin
- **Approval**: Requires superadmin approval
- **Soft Delete**: Records moved to recycle bin

---

### **15. Restore Student Form** *(New)*
- **File**: [recycle_bin.html](recycle_bin.html)
- **Purpose**: Recover deleted student records from recycle bin
- **Fields**: Confirmation checkbox, Restore reason (optional)
- **Method**: POST
- **Route**: `/restore/<student_id>`
- **Role Required**: Superadmin
- **Audit**: Logs restoration with timestamp

---

### **16. Permanent Delete Student Form** *(New)*
- **File**: [recycle_bin.html](recycle_bin.html)
- **Purpose**: Permanently delete student from system
- **Fields**: Confirmation (double checkbox), Admin password
- **Method**: POST
- **Route**: `/permanently-delete/<student_id>`
- **Role Required**: Superadmin only
- **Warning**: This action cannot be undone
- **Audit**: Logs permanent deletion

---

### **17. Student Marks Update Form** *(New)*
- **File**: [update_marks.html](update_marks.html) *(To be created)*
- **Purpose**: Update student academic marks
- **Fields**: 
  - 10th Marks, 12th Marks
  - Year 1-4 Semester marks, GPA
  - Semester/Year selection
- **Method**: POST
- **Route**: `/update-marks/<student_id>`
- **Role Required**: Admin
- **Validation**: Mark range (0-100), GPA calculation
- **Approval**: Optional superadmin approval

---

### **18. Student Attendance Form** *(New)*
- **File**: [attendance.html](attendance.html) *(To be created)*
- **Purpose**: Record/update student attendance
- **Fields**: 
  - Date range selection
  - Attendance status (Present/Absent/Leave)
  - Remarks
- **Method**: POST
- **Route**: `/attendance/<student_id>`
- **Role Required**: Admin
- **Displays**: Attendance percentage, Attendance history

---

### **19. Student Scholarship Form** *(New)*
- **File**: [scholarship_form.html](scholarship_form.html) *(To be created)*
- **Purpose**: Apply or update scholarship information
- **Fields**: 
  - Scholarship type
  - Amount
  - Start/End date
  - Remarks
- **Method**: POST
- **Route**: `/scholarship/<student_id>`
- **Role Required**: Admin
- **Validation**: Amount format, Date logic

---

### **20. Student Documents Form** *(New)*
- **File**: [student_documents.html](student_documents.html) *(To be created)*
- **Purpose**: Upload and manage student documents
- **Fields**: 
  - Document type (Birth Certificate, Aadhar, etc.)
  - File upload
  - Upload date
- **Method**: POST (multipart/form-data)
- **Route**: `/documents/<student_id>`
- **Role Required**: Admin
- **Features**: Document preview, Download, Delete

---

## ✅ **APPROVAL & REQUEST MANAGEMENT FORMS** (8 Forms)

### **21. Approval Dashboard Filter Form** *(New)*
- **File**: [approvals.html](approvals.html)
- **Purpose**: Filter pending approval requests
- **Fields**: 
  - Status: Pending, Approved, Rejected
  - Type: Edit, Delete
  - Date range
  - Requester name/ID
- **Method**: GET/POST
- **Route**: `/approvals`
- **Role Required**: Superadmin
- **Display**: Sortable approval list

---

### **22. Approve Edit Request Form**
- **File**: [approvals.html](approvals.html)
- **Purpose**: Superadmin approves student edit requests
- **Fields**: 
  - Request details (read-only comparison)
  - Approval notes (optional textarea)
  - Approval checkbox
- **Method**: POST
- **Route**: `/approve/<request_id>`
- **Role Required**: Superadmin
- **Audit**: Logs approval with timestamp & reason

---

### **23. Reject Edit Request Form**
- **File**: [approvals.html](approvals.html)
- **Purpose**: Superadmin rejects student edit requests
- **Fields**: 
  - Request details (read-only)
  - Rejection reason (required textarea)
  - Rejection checkbox
- **Method**: POST
- **Route**: `/reject/<request_id>`
- **Role Required**: Superadmin
- **Notification**: Sends notification to admin

---

### **24. Approve Delete Request Form**
- **File**: [approvals.html](approvals.html)
- **Purpose**: Superadmin approves student deletion
- **Fields**: 
  - Student details (read-only)
  - Approval notes (optional)
  - Final confirmation checkbox
- **Method**: POST
- **Route**: `/approve-delete/<request_id>`
- **Role Required**: Superadmin
- **Action**: Moves record to recycle bin

---

### **25. Reject Delete Request Form**
- **File**: [approvals.html](approvals.html)
- **Purpose**: Superadmin rejects deletion request
- **Fields**: 
  - Rejection reason (required)
  - Rejection checkbox
- **Method**: POST
- **Route**: `/reject-delete/<request_id>`
- **Role Required**: Superadmin
- **Notification**: Notifies admin of rejection

---

### **26. Request History & Timeline Form** *(New)*
- **File**: [request_timeline.html](request_timeline.html) *(To be created)*
- **Purpose**: View all past approval requests with timeline
- **Fields**: 
  - Filter by: Status, Date range, Type
  - Display: Request details, Approval/Rejection reason, Timeline
- **Method**: GET
- **Route**: `/requests/history`
- **Role Required**: Superadmin, Admin
- **Display**: Visual timeline of all requests

---

### **27. Bulk Approval Form** *(New)*
- **File**: [bulk_approval.html](bulk_approval.html) *(To be created)*
- **Purpose**: Approve multiple requests at once
- **Fields**: 
  - Select multiple requests (checkboxes)
  - Common approval notes (optional)
  - Bulk approve button
- **Method**: POST
- **Route**: `/bulk-approve`
- **Role Required**: Superadmin
- **Limit**: Max 50 requests per bulk action

---

### **28. Request Notification Preferences Form** *(New)*
- **File**: [notification_preferences.html](notification_preferences.html) *(To be created)*
- **Purpose**: Set notification preferences for approvals
- **Fields**: 
  - Email notifications
  - SMS notifications
  - Notification type selection
  - Frequency
- **Method**: POST
- **Route**: `/settings/notifications`
- **Role Required**: Superadmin, Admin
- **Persistent**: User preference stored in DB

---

## 📊 **REPORTS & ANALYTICS FORMS** (8 Forms)

### **29. Student Report Generator Form**
- **File**: [reports.html](reports.html)
- **Purpose**: Generate custom student reports
- **Fields**: 
  - Report type (All students, by college, by category, etc.)
  - Date range
  - Format (PDF, Excel, CSV)
  - Fields to include
- **Method**: POST
- **Route**: `/reports/generate`
- **Role Required**: Auditor, Superadmin
- **Features**: Export to multiple formats

---

### **30. Academic Performance Report Form** *(New)*
- **File**: [academic_report.html](academic_report.html) *(To be created)*
- **Purpose**: Analyze student academic performance
- **Fields**: 
  - Year/Semester filter
  - College filter
  - Metrics: Average GPA, Pass rate, Topper list
- **Method**: GET/POST
- **Route**: `/reports/academic`
- **Role Required**: Auditor, Superadmin
- **Display**: Charts, graphs, statistics

---

### **31. Category-wise Statistics Form** *(New)*
- **File**: [category_stats.html](category_stats.html) *(To be created)*
- **Purpose**: Category-wise student distribution
- **Fields**: 
  - Select categories: General, OBC, SC, ST
  - Show: Count, percentage, performance
- **Method**: GET/POST
- **Route**: `/reports/category-stats`
- **Role Required**: Auditor, Superadmin
- **Display**: Pie charts, statistics

---

### **32. College-wise Report Form** *(New)*
- **File**: [college_report.html](college_report.html) *(To be created)*
- **Purpose**: Report by college
- **Fields**: 
  - College selection
  - Metrics: Total students, Average GPA, Dropouts
- **Method**: GET/POST
- **Route**: `/reports/college`
- **Role Required**: Auditor, Superadmin
- **Export**: CSV, PDF

---

### **33. Attendance Report Form** *(New)*
- **File**: [attendance_report.html](attendance_report.html) *(To be created)*
- **Purpose**: Generate attendance reports
- **Fields**: 
  - Date range
  - Student/Class filter
  - Attendance threshold
- **Method**: GET/POST
- **Route**: `/reports/attendance`
- **Role Required**: Admin, Auditor
- **Display**: Attendance list, Low attendance alerts

---

### **34. Approval Audit Report Form** *(New)*
- **File**: [approval_audit.html](approval_audit.html) *(To be created)*
- **Purpose**: Audit trail of all approvals & rejections
- **Fields**: 
  - Date range
  - Approver name/ID
  - Status filter
- **Method**: GET/POST
- **Route**: `/reports/approval-audit`
- **Role Required**: Superadmin
- **Display**: Complete audit trail with timestamps

---

### **35. User Activity Report Form** *(New)*
- **File**: [activity_report.html](activity_report.html) *(To be created)*
- **Purpose**: Track user actions and activities
- **Fields**: 
  - User filter
  - Action type filter
  - Date range
- **Method**: GET/POST
- **Route**: `/reports/activity`
- **Role Required**: Superadmin
- **Display**: Detailed activity log

---

### **36. Dashboard Summary Form** *(New)*
- **File**: [dashboard_summary.html](dashboard_summary.html) *(To be created)*
- **Purpose**: Quick overview dashboard
- **Fields**: 
  - Display: Total students, Pending approvals, Recent activities
  - Quick filters
- **Method**: GET
- **Route**: `/dashboard`
- **Role Required**: All authenticated users
- **Features**: Widget-based, customizable

---

## 🔐 **ROLE & ACCESS MANAGEMENT FORMS** (8 Forms)

### **37. Change User Role Form**
- **File**: [change_role.html](change_role.html)
- **Purpose**: Superadmin changes user roles
- **Fields**: 
  - User selection
  - New role (student, admin, auditor, superadmin)
  - Role change reason
- **Method**: POST
- **Route**: `/change-role/<user_id>`
- **Role Required**: Superadmin only
- **Audit**: Logs all role changes

---

### **38. User Management Form** *(New)*
- **File**: [user_management.html](user_management.html) *(To be created)*
- **Purpose**: View and manage all users
- **Fields**: 
  - User search/filter
  - Display: Name, Email, Role, Status, Last Login
  - Actions: Edit, Deactivate, Change Role
- **Method**: GET/POST
- **Route**: `/users/manage`
- **Role Required**: Superadmin
- **Features**: Bulk actions, Export list

---

### **39. User Activation/Deactivation Form** *(New)*
- **File**: [user_management.html](user_management.html)
- **Purpose**: Activate or deactivate user accounts
- **Fields**: 
  - Reason for deactivation
  - Deactivation confirmation
- **Method**: POST
- **Route**: `/users/<user_id>/activate` or `/users/<user_id>/deactivate`
- **Role Required**: Superadmin
- **Effect**: User cannot login while deactivated

---

### **40. Assign Permissions Form** *(New)*
- **File**: [assign_permissions.html](assign_permissions.html) *(To be created)*
- **Purpose**: Assign specific permissions to roles
- **Fields**: 
  - Role selection
  - Permission checkboxes (add student, edit, delete, approve, etc.)
  - Module access control
- **Method**: POST
- **Route**: `/permissions/assign`
- **Role Required**: Superadmin
- **Features**: Predefined permission sets

---

### **41. Audit Logs & Access Report Form** *(New)*
- **File**: [audit_logs.html](audit_logs.html) *(To be created)*
- **Purpose**: View system audit logs
- **Fields**: 
  - Date range
  - User filter
  - Action type filter
  - Result status (Success/Failure)
- **Method**: GET/POST
- **Route**: `/audit-logs`
- **Role Required**: Superadmin
- **Display**: Detailed logs with timestamps, IPs, actions

---

### **42. IP Whitelist/Blacklist Form** *(New)*
- **File**: [ip_management.html](ip_management.html) *(To be created)*
- **Purpose**: Manage IP whitelist/blacklist
- **Fields**: 
  - Add/Remove IP addresses
  - IP range specification
  - Reason for whitelist/blacklist
- **Method**: POST
- **Route**: `/security/ip-management`
- **Role Required**: Superadmin
- **Features**: CIDR notation support

---

### **43. Session Management Form** *(New)*
- **File**: [session_management.html](session_management.html) *(To be created)*
- **Purpose**: Manage active user sessions
- **Fields**: 
  - View active sessions
  - Force logout option
  - Session timeout control
- **Method**: POST
- **Route**: `/sessions/manage`
- **Role Required**: Superadmin
- **Display**: Session details, duration, IP, device

---

### **44. Security Settings Form** *(New)*
- **File**: [security_settings.html](security_settings.html) *(To be created)*
- **Purpose**: Configure system security parameters
- **Fields**: 
  - Password policy
  - Session timeout duration
  - Login attempt threshold
  - 2FA requirement
- **Method**: POST
- **Route**: `/settings/security`
- **Role Required**: Superadmin
- **Persistent**: Settings stored in configuration table

---

## 🗑️ **ACCOUNT & RECYCLE MANAGEMENT FORMS** (4 Forms)

### **45. Delete Account Form**
- **File**: [delete_account.html](delete_account.html)
- **Purpose**: User deletes their own account
- **Fields**: 
  - Password confirmation
  - Account deletion reason
  - Final confirmation checkbox
- **Method**: POST
- **Route**: `/remove-account`
- **Access**: All authenticated users
- **Effect**: Account deactivated, data moved to archive

---

### **46. Recycle Bin Management Form**
- **File**: [recycle_bin.html](recycle_bin.html)
- **Purpose**: View and manage deleted records
- **Fields**: 
  - Filter by: Deletion date, Record type, Deleted by
  - Display: Record details, Deletion date, Delete by user
  - Actions: Restore, Permanently delete
- **Method**: GET/POST
- **Route**: `/recycle-bin`
- **Role Required**: Superadmin, Admin
- **Features**: Auto-purge after 30 days

---

### **47. Restore from Recycle Form**
- **File**: [recycle_bin.html](recycle_bin.html)
- **Purpose**: Restore deleted student records
- **Fields**: 
  - Record selection
  - Restoration reason (optional)
  - Final confirmation
- **Method**: POST
- **Route**: `/restore`
- **Role Required**: Superadmin, Admin
- **Audit**: Logs restoration event

---

### **48. Permanent Deletion Form**
- **File**: [recycle_bin.html](recycle_bin.html)
- **Purpose**: Permanently delete records from system
- **Fields**: 
  - Record selection
  - Double confirmation (two checkboxes)
  - Admin password
  - Deletion reason
- **Method**: POST
- **Route**: `/permanently-delete`
- **Role Required**: Superadmin only
- **Warning**: Irreversible action
- **Audit**: Logs permanent deletion with reason

---

## 📝 **LOGGING & MONITORING FORMS** (2 Forms)

### **49. User Activity Logs Form**
- **File**: [logs.html](logs.html)
- **Purpose**: View detailed activity logs
- **Fields**: 
  - User filter
  - Date range
  - Action type filter (Login, Edit, Delete, Approve, etc.)
  - Result filter (Success/Failure)
- **Method**: GET/POST
- **Route**: `/logs`
- **Role Required**: Admin, Auditor, Superadmin
- **Features**: Export to CSV, Real-time updates

---

### **50. System Health & Performance Form** *(New)*
- **File**: [system_health.html](system_health.html) *(To be created)*
- **Purpose**: Monitor system health and performance
- **Fields**: 
  - Database connection status
  - API response time
  - Active users count
  - Error rate monitoring
  - System resource usage
- **Method**: GET
- **Route**: `/system/health`
- **Role Required**: Superadmin
- **Display**: Real-time metrics, Alerts

---

## 📊 Form Summary by Category

### 🔐 **Authentication Forms** (8)
1. Login | 2. Register | 3. OTP Verification | 4. Resend OTP | 5. Forgot Password | 6. Reset Password | 7. Change Password | 8. 2FA Setup

### 👥 **Student Management** (12)
9. Add Student | 10. Edit Student | 11. Bulk Upload | 12. Search & Filter | 13. Student Profile | 14. Delete Student | 15. Restore Student | 16. Permanent Delete | 17. Update Marks | 18. Attendance | 19. Scholarship | 20. Documents

### ✅ **Approval & Requests** (8)
21. Approval Dashboard | 22. Approve Edit | 23. Reject Edit | 24. Approve Delete | 25. Reject Delete | 26. Request History | 27. Bulk Approval | 28. Notification Preferences

### 📊 **Reports & Analytics** (8)
29. Student Report | 30. Academic Performance | 31. Category Statistics | 32. College Report | 33. Attendance Report | 34. Approval Audit | 35. User Activity | 36. Dashboard Summary

### 🔐 **Role & Access** (8)
37. Change Role | 38. User Management | 39. Activate/Deactivate | 40. Assign Permissions | 41. Audit Logs | 42. IP Management | 43. Session Management | 44. Security Settings

### 🗑️ **Account & Recycle** (4)
45. Delete Account | 46. Recycle Bin | 47. Restore Records | 48. Permanent Delete

### 📝 **Logging & Monitoring** (2)
49. Activity Logs | 50. System Health

---

## Forms by Role Access

| Form | Student | Admin | Auditor | Superadmin |
|------|---------|-------|---------|-----------|
| Login | ✅ | ✅ | ✅ | ✅ |
| Register | ✅ | ✅ | ✅ | ✅ |
| OTP Verification | ✅ | ✅ | ✅ | ✅ |
| Forgot Password | ✅ | ✅ | ✅ | ✅ |
| Reset Password | ✅ | ✅ | ✅ | ✅ |
| Add Student | ❌ | ✅ | ❌ | ❌ |
| Edit Student | ❌ | ✅ | ❌ | ❌ |
| Delete Student | ❌ | ✅ | ❌ | ❌ |
| Approve Request | ❌ | ❌ | ❌ | ✅ |
| Reject Request | ❌ | ❌ | ❌ | ✅ |
| Change Role | ❌ | ❌ | ❌ | ✅ |
| Delete Account | ✅ | ✅ | ✅ | ✅ |


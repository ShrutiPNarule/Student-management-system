# 📋 Forms in Student Management System

## Total Forms: **12 Forms**

---

### **1. Login Form** 
- **File**: [login.html](login.html)
- **Purpose**: User authentication
- **Fields**: Email, Password, Remember Me checkbox
- **Method**: POST
- **Route**: `/login`

---

### **2. Register Form**
- **File**: [register.html](register.html)
- **Purpose**: New user account creation
- **Fields**: Name, Email, Password, Phone, Address/College
- **Method**: POST
- **Route**: `/register`

---

### **3. OTP Verification Form**
- **File**: [verify_otp.html](verify_otp.html)
- **Purpose**: Verify OTP during login
- **Fields**: OTP Code, Remember Me checkbox
- **Method**: POST
- **Route**: `/verify-otp`

---

### **4. Forgot Password Form**
- **File**: [forgot_password.html](forgot_password.html)
- **Purpose**: Request password reset
- **Fields**: Email
- **Method**: POST
- **Route**: `/forgot-password`

---

### **5. Reset Password Form**
- **File**: [reset_password.html](reset_password.html)
- **Purpose**: Set new password using reset token
- **Fields**: New Password, Confirm Password
- **Method**: POST
- **Route**: `/reset-password`

---

### **6. Add Student Form**
- **File**: [add_student.html](add_student.html)
- **Purpose**: Admin adds new student record (Admin only)
- **Fields**: 
  - Name, Roll Number, College
  - Phone, Email
  - Marks (10th, 12th, Year 1-4)
- **Method**: POST
- **Route**: `/add`
- **Role Required**: Admin

---

### **7. Edit Student Form**
- **File**: [edit_student.html](edit_student.html)
- **Purpose**: Admin requests to edit student data (Admin only)
- **Fields**:
  - Name, Roll Number, College
  - Phone, Email
  - Marks (10th, 12th, Year 1-4)
- **Method**: POST
- **Route**: `/edit/<student_id>`
- **Role Required**: Admin
- **Note**: Creates approval request for superadmin

---

### **8. Delete Student Form**
- **File**: [index.html](index.html) (inline form)
- **Purpose**: Admin requests to delete student data (Admin only)
- **Fields**: None (hidden confirmation)
- **Method**: POST
- **Route**: `/delete/<student_id>`
- **Role Required**: Admin
- **Note**: Creates approval request for superadmin

---

### **9. Approval Form** (Approve Button)
- **File**: [approvals.html](approvals.html)
- **Purpose**: Superadmin approves edit/delete requests
- **Fields**: Approval notes (optional textarea)
- **Method**: POST
- **Route**: `/approve/<request_id>`
- **Role Required**: Superadmin

---

### **10. Rejection Form** (Reject Button)
- **File**: [approvals.html](approvals.html)
- **Purpose**: Superadmin rejects edit/delete requests
- **Fields**: Rejection reason (required textarea)
- **Method**: POST
- **Route**: `/reject/<request_id>`
- **Role Required**: Superadmin

---

### **11. Change Role Form**
- **File**: [change_role.html](change_role.html)
- **Purpose**: Superadmin changes user role
- **Fields**: Role dropdown (student, admin, auditor, superadmin)
- **Method**: POST
- **Route**: `/change-role/<user_id>`
- **Role Required**: Superadmin

---

### **12. Delete Account Form**
- **File**: [delete_account.html](delete_account.html)
- **Purpose**: User deletes their own account
- **Fields**: Password confirmation
- **Method**: POST
- **Route**: `/remove-account`

---

## Form Summary by Category

### 🔐 **Authentication Forms** (5)
1. Login
2. Register
3. OTP Verification
4. Forgot Password
5. Reset Password

### 👥 **Student Management Forms** (4)
6. Add Student (Admin)
7. Edit Student (Admin)
8. Delete Student (Admin) 
9. Change Role (Superadmin)

### ✅ **Approval Forms** (2)
10. Approve Request (Superadmin)
11. Reject Request (Superadmin)

### 🗑️ **Account Management** (1)
12. Delete Account (User)

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


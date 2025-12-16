# Database Schema Update - Migration Summary

## Changes Made to db.py
1. **Added `password` column to users table** - Now stores hashed passwords
2. **Added student management tables**:
   - `students_master` - Stores student info with soft delete support
   - `student_marks` - Stores student marks with soft delete support

## Updated Files

### Authentication Routes
- **login_route.py**: Updated to query new users table structure (id TEXT, email, role_id)
- **register_route.py**: Updated to insert into new users table with password hashing
- **verify_otp.py**: No changes needed, works with new structure

### Student Management Routes  
- **add_route.py**: Added log_action calls, maintains existing functionality
- **edit_route.py**: Added log_action calls, maintains existing functionality
- **delete_route.py**: Simplified by removing restore functionality, uses log_action
- **index_route.py**: Updated to use correct table names and role comparisons

### Activity Logging
- **log_utils.py**: Complete rewrite to use new activity_log table with user_id, action, entity_type, metadata
- **log_route.py**: Updated queries to match new activity_log table structure

### Account Management
- **remove_logged_account.py**: Updated to use user_id from session and new users table

### Other Updates
- **routes/__init__.py**: Updated RBAC decorator documentation to use lowercase role names
- **base.html**: Updated role checks to use lowercase ("admin", "auditor")
- **index.html**: Updated role checks to lowercase
- **add_student.html**: Updated role checks to lowercase
- **edit_student.html**: Updated role checks to lowercase
- **logs.html**: Updated role checks to lowercase
- **recycle_bin.html**: Updated role checks to lowercase
- **requirements.txt**: Added werkzeug and python-dotenv dependencies

## Key Changes Summary

### Table Structure
| Old | New |
|-----|-----|
| users.user_id | users.id (TEXT with custom sequence) |
| users.password (missing) | users.password (TEXT) |
| roles.role_id (INT) | roles.id (TEXT with custom sequence) |
| roles.role_name | roles.name |
| activity_logs | activity_log (new structure) |

### Role Names
All role names are now **lowercase**: "admin", "auditor", "general"

### Session Keys
- user_id: `session["user_id"]` (TEXT)
- user_email: `session["user_email"]`
- role: `session["role"]` (lowercase)

### Logging
New log_action signature:
```python
log_action(action, entity_type="", entity_id="", metadata=None)
```

Examples:
```python
log_action("CREATE", "STUDENT", "5", {"name": "John"})
log_action("DELETE", "STUDENT", "5")
log_action("ACCOUNT_DELETE", "USER", user_id)
```

## Setup Instructions

1. **Run db.py** to create new tables and sequences
2. **Run init_db.py** to initialize roles:
   ```bash
   python init_db.py
   ```
3. **Update your .env** if needed
4. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Start the Flask app**:
   ```bash
   python app.py
   ```

## Important Notes
- All role names must be lowercase in code and database
- The users table now requires a password field
- Activity logging uses JSONB for metadata
- Student management still uses SERIAL INT for student IDs (not TEXT)

# Debug: Edit Data Not Showing on Home Page

## Root Cause Identified

### The Problem
When admin approves an edited student record, the data is updated in the database but doesn't show on the home page.

### Why It's Happening

1. **Form sends "college"** → Stored in `change_data["college"]`
2. **Admin approval code maps it incorrectly**:
   ```python
   # Currently (WRONG):
   address = change_data.get("college")  # College goes into ADDRESS field!
   
   cur.execute("""UPDATE users_master SET address = %s WHERE id = %s""", 
               (college_value, user_id))
   ```

3. **Home page query expects college from**:
   - `colleges_master` via `college_enrollment` table
   - NOT from `users_master.address`

### The Fix
We need to:
1. Store college properly in `colleges_master` / `college_enrollment`
2. OR store it in a dedicated field (currently using `address` is incorrect)
3. Update the mapping in `admin_approval_workflow.py`

### What's Being Updated (Current Buggy Code)
```
users_master.address ← college value (WRONG!)
users_master.name ← name ✓
users_master.phone ← phone ✓
users_master.email ← email ✓
users_master.dob ← dob ✓
users_master.category ← category ✓
users_master.birth_place ← birth_place ✓
```

### What Should Be Updated
```
users_master.name ← name ✓
users_master.phone ← phone ✓
users_master.email ← email ✓
users_master.address ← address (if we have it)
users_master.dob ← dob ✓
users_master.category ← category ✓
users_master.birth_place ← birth_place ✓

college_enrollment ← college (Need to link student to college)
```

## Solution Steps

1. Fix `admin_approval_workflow.py` to NOT put college in address
2. Add proper college handling via `college_enrollment` table
3. Test that home page shows updated data

## Status: PENDING FIX

#!/usr/bin/env python
"""Create trigger to sync students_master when role changes"""
from db import get_connection

conn = get_connection()
cur = conn.cursor()

try:
    # Create trigger function to handle role changes
    cur.execute("""
        CREATE OR REPLACE FUNCTION handle_role_change()
        RETURNS TRIGGER AS $trigger$
        DECLARE
            student_role_id TEXT;
        BEGIN
            -- Get the student role ID
            SELECT id INTO student_role_id FROM roles_master WHERE name = 'student' LIMIT 1;
            
            -- If role is changed TO student
            IF NEW.role_id = student_role_id AND OLD.role_id IS DISTINCT FROM NEW.role_id THEN
                -- Create entry in students_master if doesn't exist
                INSERT INTO students_master (user_id, current_status)
                VALUES (NEW.id, 'active')
                ON CONFLICT DO NOTHING;
            
            -- If role is changed FROM student to something else
            ELSIF OLD.role_id = student_role_id AND NEW.role_id IS DISTINCT FROM OLD.role_id THEN
                -- Delete from students_master
                DELETE FROM students_master WHERE user_id = NEW.id;
            END IF;
            
            RETURN NEW;
        END;
        $trigger$ LANGUAGE plpgsql;
    """)
    
    # Drop existing trigger if it exists
    cur.execute('DROP TRIGGER IF EXISTS role_change_trigger ON users_master')
    
    # Create trigger
    cur.execute("""
        CREATE TRIGGER role_change_trigger
        AFTER UPDATE OF role_id ON users_master
        FOR EACH ROW
        EXECUTE FUNCTION handle_role_change();
    """)
    
    conn.commit()
    print('✅ Trigger created successfully!')
    print('')
    print('📌 How it works:')
    print('   • When role is changed TO student: Entry CREATED in students_master')
    print('   • When role is changed FROM student: Entry DELETED from students_master')
    print('   • Works for ANY change (pgAdmin, application, or direct SQL)')
    print('')
    print('🔄 Now all data stays in sync automatically!')
    
except Exception as e:
    conn.rollback()
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()

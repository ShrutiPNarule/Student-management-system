#!/usr/bin/env python
"""Check superadmin permissions"""
from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute('''
    SELECT 
        name,
        view_student,
        add_student,
        delete_student,
        change_user_role,
        add_marks,
        view_activity_log,
        create_application,
        approve_application
    FROM roles_master
    WHERE name = 'superadmin'
''')

result = cur.fetchone()
if result:
    name, view, add_st, del_st, change_role, add_marks, view_log, create_app, approve_app = result
    print('='*70)
    print('🔐 SUPERADMIN PERMISSIONS')
    print('='*70)
    print(f'\nRole: {name.upper()}')
    print('\nPermissions:')
    
    perms = [
        ('View Student', view),
        ('Add Student', add_st),
        ('Delete Student', del_st),
        ('Change User Role', change_role),
        ('Add Marks', add_marks),
        ('View Activity Log', view_log),
        ('Create Application', create_app),
        ('Approve Application', approve_app),
    ]
    
    for perm_name, perm_value in perms:
        status = '✅ YES' if perm_value else '❌ NO'
        print(f'  • {perm_name}: {status}')
    
    print('\n' + '='*70)
    
    # Show all roles for comparison
    print('\n📊 ALL ROLES PERMISSIONS COMPARISON:')
    print('='*70)
    
    cur.execute('''
        SELECT 
            name,
            view_student,
            add_student,
            delete_student,
            change_user_role,
            add_marks,
            view_activity_log,
            create_application,
            approve_application
        FROM roles_master
        ORDER BY name
    ''')
    
    roles = cur.fetchall()
    
    print(f"\n{'Role':<15} {'View':<6} {'Add':<6} {'Delete':<8} {'ChgRole':<8} {'Marks':<6} {'Log':<6} {'Create':<8} {'Approve':<8}")
    print('-'*80)
    
    for role_data in roles:
        role_name = role_data[0]
        perms = ['✅' if p else '❌' for p in role_data[1:]]
        print(f"{role_name:<15} {perms[0]:<6} {perms[1]:<6} {perms[2]:<8} {perms[3]:<8} {perms[4]:<6} {perms[5]:<6} {perms[6]:<8} {perms[7]:<8}")
    
    print('='*70)
else:
    print('❌ Superadmin role not found')

cur.close()
conn.close()

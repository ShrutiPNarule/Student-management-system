"""
Verify the role permissions after transfer
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    connect_timeout=5
)
cur = conn.cursor()

print("[DB] Database connection established\n")

# Check all roles and their permissions
cur.execute("""
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
""")

roles = cur.fetchall()

print("="*80)
print("📊 ALL ROLES WITH PERMISSIONS")
print("="*80)
print(f"\n{'Role':<15} {'View':<6} {'Add':<6} {'Delete':<8} {'ChgRole':<8} {'Marks':<6} {'Log':<6} {'Create':<8} {'Approve':<8}")
print("-"*80)

for role_data in roles:
    role_name = role_data[0]
    view = "✅" if role_data[1] else "❌"
    add = "✅" if role_data[2] else "❌"
    delete = "✅" if role_data[3] else "❌"
    change_role = "✅" if role_data[4] else "❌"
    marks = "✅" if role_data[5] else "❌"
    log = "✅" if role_data[6] else "❌"
    create = "✅" if role_data[7] else "❌"
    approve = "✅" if role_data[8] else "❌"
    
    print(f"{role_name:<15} {view:<6} {add:<6} {delete:<8} {change_role:<8} {marks:<6} {log:<6} {create:<8} {approve:<8}")

print("="*80)

# Check users and their roles
cur.execute("""
    SELECT u.id, u.name, r.name as role
    FROM users_master u
    LEFT JOIN roles_master r ON u.role_id = r.id
    ORDER BY u.id
""")

users = cur.fetchall()

print(f"\n📋 USERS AND THEIR ROLES")
print("="*80)
print(f"{'User ID':<12} {'Name':<30} {'Role':<20}")
print("-"*80)

for user_id, user_name, role_name in users:
    print(f"{user_id:<12} {user_name:<30} {role_name:<20}")

print("="*80)

cur.close()
conn.close()

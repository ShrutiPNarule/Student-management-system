#!/usr/bin/env python3
"""
List all users in the database
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def list_all_users():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        
        print("=" * 80)
        print("ALL USERS IN DATABASE")
        print("=" * 80)
        
        cur.execute("""
            SELECT u.id, u.name, u.email, u.role_id, r.name as role_name
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            ORDER BY u.created_at DESC
        """)
        
        users = cur.fetchall()
        
        if not users:
            print("\n❌ No users found in database")
            cur.close()
            conn.close()
            return
        
        print(f"\n📋 Total Users: {len(users)}\n")
        print(f"{'ID':<12} {'Name':<20} {'Email':<30} {'Role':<15}")
        print("-" * 80)
        
        for user_id, name, email, role_id, role_name in users:
            print(f"{user_id:<12} {name:<20} {email:<30} {role_name.upper():<15}")
        
        print("\n" + "=" * 80)
        
        cur.close()
        conn.close()
        
    except Exception as error:
        print(f"❌ ERROR: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_all_users()

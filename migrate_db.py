# ============================================================
# DATABASE MIGRATION SCRIPT
# Automatically creates missing tables and columns
# ============================================================

import psycopg2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    """Run all database migrations"""
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
        )
        cur = conn.cursor()
        
        print("🔄 Running database migrations...")
        
        # ============================================================
        # MIGRATION 1: Add account lockout columns to users_master
        # ============================================================
        print("  ✓ Adding lockout columns to users_master...")
        try:
            cur.execute("""
                ALTER TABLE users_master
                ADD COLUMN IF NOT EXISTS failed_login_attempts INT DEFAULT 0;
            """)
            print("    ✓ failed_login_attempts column added")
        except psycopg2.Error as e:
            print(f"    ⚠ {e}")
        
        try:
            cur.execute("""
                ALTER TABLE users_master
                ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP;
            """)
            print("    ✓ locked_until column added")
        except psycopg2.Error as e:
            print(f"    ⚠ {e}")
        
        # ============================================================
        # MIGRATION 2: Create password_reset_tokens table
        # ============================================================
        print("  ✓ Creating password_reset_tokens table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id SERIAL PRIMARY KEY,
                user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("    ✓ password_reset_tokens table created")
        
        # ============================================================
        # MIGRATION 3: Create persistent_tokens table
        # ============================================================
        print("  ✓ Creating persistent_tokens table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS persistent_tokens (
                id SERIAL PRIMARY KEY,
                user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("    ✓ persistent_tokens table created")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Database migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)

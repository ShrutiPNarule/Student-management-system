"""
Database Migration Script
Runs on app startup to add missing columns and tables
"""
import psycopg2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    """Run all pending database migrations"""
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
        )
        cur = conn.cursor()

        print("[MIGRATION] Starting database migrations...")

        # ==========================================
        # Migration 1: Add failed_login_attempts column
        # ==========================================
        try:
            cur.execute("""
                ALTER TABLE users_master 
                ADD COLUMN IF NOT EXISTS failed_login_attempts INT DEFAULT 0;
            """)
            conn.commit()
            print("[MIGRATION] ✅ Added 'failed_login_attempts' column to users_master")
        except psycopg2.Error as e:
            print(f"[MIGRATION] ⚠️  failed_login_attempts: {e}")
            conn.rollback()

        # ==========================================
        # Migration 2: Add locked_until column
        # ==========================================
        try:
            cur.execute("""
                ALTER TABLE users_master 
                ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP;
            """)
            conn.commit()
            print("[MIGRATION] ✅ Added 'locked_until' column to users_master")
        except psycopg2.Error as e:
            print(f"[MIGRATION] ⚠️  locked_until: {e}")
            conn.rollback()

        # ==========================================
        # Migration 3: Create password_reset_tokens table
        # ==========================================
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("[MIGRATION] ✅ Created 'password_reset_tokens' table")
        except psycopg2.Error as e:
            print(f"[MIGRATION] ⚠️  password_reset_tokens: {e}")
            conn.rollback()

        # ==========================================
        # Migration 4: Create persistent_tokens table
        # ==========================================
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS persistent_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("[MIGRATION] ✅ Created 'persistent_tokens' table")
        except psycopg2.Error as e:
            print(f"[MIGRATION] ⚠️  persistent_tokens: {e}")
            conn.rollback()

        print("[MIGRATION] ✅ All migrations completed successfully!")
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"[MIGRATION] ❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)

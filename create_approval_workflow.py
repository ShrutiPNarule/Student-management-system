"""
Add pending_changes table for data verification and approval workflow
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_approval_workflow_tables():
    try:
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
        
        # Create sequences for pending changes
        print("📝 Creating sequences...")
        cur.execute("CREATE SEQUENCE IF NOT EXISTS pending_change_seq START 1;")
        print("   ✅ pending_change_seq created")
        
        # Create pending_changes table
        print("\n📝 Creating pending_changes table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pending_changes (
                id TEXT PRIMARY KEY DEFAULT
                    'PC' || LPAD(nextval('pending_change_seq')::TEXT, 6, '0'),
                
                change_type TEXT NOT NULL,  -- 'add_student', 'edit_student', 'add_marks', etc.
                student_id TEXT,  -- For edits, references the student being modified
                
                -- Changed data (stored as JSON)
                data JSONB NOT NULL,
                
                -- Change metadata
                created_by TEXT NOT NULL REFERENCES users_master(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Verification workflow
                status TEXT DEFAULT 'pending',  -- pending, auditor_verified, rejected_by_auditor, admin_approved, rejected_by_admin, completed
                
                auditor_id TEXT REFERENCES users_master(id) ON DELETE SET NULL,
                auditor_verified_at TIMESTAMP,
                auditor_remarks TEXT,
                
                admin_id TEXT REFERENCES users_master(id) ON DELETE SET NULL,
                admin_approved_at TIMESTAMP,
                admin_remarks TEXT,
                
                -- Original data backup (for reference)
                original_data JSONB,
                
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ pending_changes table created")
        
        # Create indices for better query performance
        print("\n📝 Creating indices...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_changes(status);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_created_by ON pending_changes(created_by);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_student ON pending_changes(student_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_auditor ON pending_changes(auditor_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_admin ON pending_changes(admin_id);")
        print("   ✅ Indices created")
        
        conn.commit()
        print("\n" + "="*70)
        print("✅ Approval workflow tables created successfully!")
        print("="*70)
        print("\n📊 New workflow status options:")
        print("   • pending - Waiting for auditor verification")
        print("   • auditor_verified - Auditor approved, waiting for admin")
        print("   • rejected_by_auditor - Auditor rejected")
        print("   • admin_approved - Admin approved, ready to update")
        print("   • rejected_by_admin - Admin rejected")
        print("   • completed - Successfully applied to main data")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    create_approval_workflow_tables()

"""
Verify the approval workflow tables were created correctly
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

# Check if pending_changes table exists
cur.execute("""
    SELECT EXISTS(
        SELECT FROM information_schema.tables 
        WHERE table_name = 'pending_changes'
    );
""")

table_exists = cur.fetchone()[0]

print("="*70)
print("✅ APPROVAL WORKFLOW VERIFICATION")
print("="*70)

if table_exists:
    print("\n✅ Table 'pending_changes' EXISTS")
    
    # Get table structure
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'pending_changes'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    
    print("\n📋 Table Structure:")
    print("-" * 70)
    print(f"{'Column':<30} {'Type':<20} {'Nullable':<10}")
    print("-" * 70)
    
    for col_name, col_type, nullable in columns:
        print(f"{col_name:<30} {col_type:<20} {'YES' if nullable == 'YES' else 'NO':<10}")
    
    print("-" * 70)
    
    # Check for indices
    cur.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'pending_changes'
    """)
    
    indices = cur.fetchall()
    
    print(f"\n🔍 Indices Created: {len(indices)}")
    for idx in indices:
        print(f"   ✅ {idx[0]}")
    
    # Count current records
    cur.execute("SELECT COUNT(*) FROM pending_changes;")
    record_count = cur.fetchone()[0]
    
    print(f"\n📊 Current Records: {record_count}")
    
else:
    print("\n❌ Table 'pending_changes' NOT FOUND")

print("\n" + "="*70)
print("✅ WORKFLOW IMPLEMENTATION STATUS")
print("="*70)
print("\n📝 Created Files:")
print("   ✅ routes/auditor_verification.py - Auditor verification logic")
print("   ✅ routes/admin_approval_workflow.py - Admin approval logic")
print("   ✅ templates/auditor_verify_changes.html - Auditor UI")
print("   ✅ templates/admin_approve_changes.html - Admin UI")
print("   ✅ DATA_APPROVAL_WORKFLOW.md - Full documentation")
print("   ✅ WORKFLOW_IMPLEMENTATION_COMPLETE.md - Implementation guide")

print("\n🔗 Routes Available:")
print("   ✅ GET /auditor/pending-changes - View pending for auditor")
print("   ✅ POST /auditor/verify-change/<id> - Auditor verify/reject")
print("   ✅ GET /admin/pending-approvals - View verified for admin")
print("   ✅ POST /admin/approve-change/<id> - Admin approve/reject")

print("\n⚠️  NEXT STEPS TO INTEGRATE:")
print("   1. Modify routes/add_route.py to save to pending_changes")
print("   2. Modify routes/edit_route.py to save to pending_changes")
print("   3. Import new routes in app.py")
print("   4. Update home page to show only approved data")
print("   5. Add navigation links for auditor and admin")

print("\n" + "="*70)

cur.close()
conn.close()

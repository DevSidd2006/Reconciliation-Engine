from db.database import Base, engine
from models.transaction import Transaction
from models.mismatch import Mismatch

print("🏦 Recreating banking reconciliation tables...")
print("⚠️  This will drop existing tables and recreate them")

try:
    # Drop all tables
    print("🗑️  Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Create new tables with updated schema
    print("📋 Creating new transaction table with reconciliation fields...")
    print("🚨 Creating new mismatch table with severity tracking...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables recreated successfully!")
    print("   - transactions (with reconciliation status, audit fields)")
    print("   - mismatches (with severity, resolution tracking, audit fields)")
    
except Exception as e:
    print(f"❌ Error recreating tables: {e}")
    print("Make sure PostgreSQL is running and .env file is configured correctly")
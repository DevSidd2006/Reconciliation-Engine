from db.database import Base, engine
from models.transaction import Transaction
from models.mismatch import Mismatch

print("🏦 Creating banking reconciliation tables...")
print("📋 Transaction table with reconciliation fields...")
print("🚨 Mismatch table with severity tracking...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("   - transactions (with reconciliation status)")
    print("   - mismatches (with severity and resolution tracking)")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    print("Make sure PostgreSQL is running and .env file is configured correctly")
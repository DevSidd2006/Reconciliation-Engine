#!/usr/bin/env python3
"""
Database table creation script for Banking Reconciliation Engine
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.database import engine, Base
from app.models.transaction import Transaction
from app.models.mismatch import Mismatch

def create_tables():
    """Create all database tables"""
    try:
        print("🏗️ Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("📊 Tables created:")
        print("   - transactions")
        print("   - mismatches")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n🎉 Database initialization complete!")
    else:
        print("\n💥 Database initialization failed!")
        sys.exit(1)
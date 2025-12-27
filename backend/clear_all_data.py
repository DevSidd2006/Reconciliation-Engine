#!/usr/bin/env python3
"""
Clear All Transaction Data
Removes all transactions and mismatches from the database for a fresh start
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.database import SessionLocal
from app.models.transaction import Transaction
from app.models.mismatch import Mismatch

def clear_all_data():
    """Clear all transactions and mismatches from database"""
    db = SessionLocal()
    try:
        print("🗑️ Clearing all transaction data...")
        
        # Count existing records
        transaction_count = db.query(Transaction).count()
        mismatch_count = db.query(Mismatch).count()
        
        print(f"📊 Found {transaction_count:,} transactions and {mismatch_count:,} mismatches")
        
        # Delete all mismatches first (foreign key constraint)
        deleted_mismatches = db.query(Mismatch).delete()
        print(f"🗑️ Deleted {deleted_mismatches:,} mismatches")
        
        # Delete all transactions
        deleted_transactions = db.query(Transaction).delete()
        print(f"🗑️ Deleted {deleted_transactions:,} transactions")
        
        # Commit the changes
        db.commit()
        
        print("✅ All transaction data cleared successfully!")
        print("🚀 Ready for fresh data generation")
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_data()
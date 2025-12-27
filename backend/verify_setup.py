import sys
import os
sys.path.append(os.path.join(os.getcwd(), "app"))

from db.database import SessionLocal, engine
from security import AuditLog
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_setup():
    print("--- Verifying System Setup ---")
    
    # 1. Check Database & Audit Table
    try:
        db = SessionLocal()
        # Try a simple select or insert
        db.execute(text("SELECT count(*) FROM audit_logs"))
        print("✅ Database Connection: OK")
        print("✅ Table 'audit_logs': FOUND (Fix confirmed)")
    except Exception as e:
        print(f"❌ Database Error: {e}")
        print("   (Did you run init_db.py?)")
    finally:
        db.close()

    # 2. Check Redis (Optional)
    try:
        from utils.redis import redis_client
        if redis_client.ping():
            print("✅ Redis: CONNECTED")
        else:
            print("⚠️  Redis: UNAVAILABLE (Running in degraded mode)")
    except Exception as e:
        print(f"⚠️  Redis: UNAVAILABLE ({e})")
        print("   (This is fine, the app will just run without rate limiting)")

if __name__ == "__main__":
    check_setup()

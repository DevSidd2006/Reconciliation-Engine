from db.database import engine, SessionLocal
from sqlalchemy import text

print("🔍 Testing database connection...")

try:
    # Test engine connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Engine connection successful")
    
    # Test session
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        print("✅ Session connection successful")
        
        # Test table existence
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print(f"📋 Tables found: {tables}")
        
    finally:
        db.close()
        
    print("🎉 Database connection is working!")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("Make sure PostgreSQL is running and credentials are correct")
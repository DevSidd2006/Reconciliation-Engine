import sys
import os
sys.path.append(os.path.join(os.getcwd(), "app"))

from db.database import engine, Base
from models.transaction import Transaction
from models.mismatch import Mismatch
from security import AuditLog
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info(f"Connecting to database via: {engine.url}")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        # Hint about port mismatch if connection refused
        if "Connection refused" in str(e):
            logger.warning("HINT: If you are running Docker, check if your .env points to the correct mapped port (e.g. 5433 instead of 5432).")

if __name__ == "__main__":
    init_db()

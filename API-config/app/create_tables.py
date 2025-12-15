from db.database import Base, engine
from models.transaction import Transaction
from models.mismatch import Mismatch

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
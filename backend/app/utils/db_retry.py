import time
from sqlalchemy.exc import OperationalError

def retry_db_operation(func, retries=3, delay=1):
    for attempt in range(retries):
        try:
            return func()
        except OperationalError:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise RuntimeError("Database unavailable after retries.")
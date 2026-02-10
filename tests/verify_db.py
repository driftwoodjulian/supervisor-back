import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import eval_engine, source_engine
from sqlalchemy import text

def test_connections():
    print("Testing Source DB Connection (Postgres)...")
    try:
        with source_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"Source DB Success: {result.fetchone()}")
    except Exception as e:
        print(f"Source DB Failed: {e}")

    print("\nTesting Eval DB Connection (SQLite)...")
    try:
        with eval_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"Eval DB Success: {result.fetchone()}")
            
            # Check if tables exist
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='evaluations'"))
            print(f"Evaluations Table Exists: {result.fetchone() is not None}")
    except Exception as e:
        print(f"Eval DB Failed: {e}")

if __name__ == "__main__":
    test_connections()

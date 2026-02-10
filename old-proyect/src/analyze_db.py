from sqlalchemy import create_engine, text
import json
import sys

# READ-ONLY Analysis Script

# Configuration from src/app.py
DB_URI = "postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/towebs"

def analyze_database():
    print("Connecting to database...")
    try:
        engine = create_engine(DB_URI)
        conn = engine.connect()
        print("Connection successful.")
        
        # 1. Count messages
        print("\n--- Message Statistics ---")
        result = conn.execute(text("SELECT count(*) FROM chats.message"))
        count = result.scalar()
        print(f"Total Messages: {count}")
        
        # 2. Check recent messages and their AUTHOR field
        print("\n--- Recent Support Messages (Author Structure) ---")
        # querying for messages where author is not a simple string (which usually implies customer)
        # We'll just fetch a few and print them to see the structure.
        query = text('SELECT id, "chatId", "text", "author" FROM chats.message WHERE "author"::text LIKE \'{%\' LIMIT 5')
        result = conn.execute(query)
        for row in result:
            print(f"Chat {row.chatId} Author: {row.author}")

        # 3. Connection is read-only by intent (we do not commit).
        # We also explicitly avoid any DROP/INSERT/UPDATE in this script.
        
        conn.close()
        print("\nAnalysis complete.")
        
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    analyze_database()

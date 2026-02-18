import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

SOURCE_DB_URI = os.getenv("SOURCE_DB_URI")
if not SOURCE_DB_URI:
    print("SOURCE_DB_URI not found in environment variables")
    exit(1)

engine = create_engine(SOURCE_DB_URI)

def analyze_messages():
    with engine.connect() as conn:
        print("--- Inspecting 'chats.message' columns ---")
        try:
            result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'chats' AND table_name = 'message'"))
            for row in result:
                print(row)
        except Exception as e:
            print(f"Error inspecting columns: {e}")

        print("\n--- Grouping by 'type' ---")
        try:
            result = conn.execute(text("SELECT type, COUNT(*) FROM chats.message GROUP BY type"))
            for row in result:
                print(row)
        except Exception as e:
            print(f"Error grouping by type: {e}")

        print("\n--- Checking for 'Attachment' table ---")
        try:
            result = conn.execute(text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name ILIKE '%attachment%'"))
            tables = result.fetchall()
            if not tables:
                print("No table found matching '%attachment%'.")
            else:
                for schema, name in tables:
                    print(f"Found table: {schema}.{name}")
                    
                    # Inspect columns of the found table
                    print(f"Columns in {schema}.{name}:")
                    cols = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{name}'"))
                    for col in cols:
                        print(col)
        except Exception as e:
            print(f"Error checking tables: {e}")

        print("\n--- Inspecting Chat 18345 ---")
        try:
            # Get messages for this chat
            query = text("""
                SELECT id, type, "attachmentId", metadata, text
                FROM chats.message 
                WHERE "chatId" = 18345
                ORDER BY "createdAt"
            """)
            result = conn.execute(query)
            rows = result.fetchall()
            if not rows:
                print("No messages found for chat 18345.")
            else:
                print(f"Found {len(rows)} messages for chat 18345.")
                for row in rows:
                    if row.type == 'image' or row.attachmentId is not None:
                        print(f"msg_id: {row.id}")
                        print(f"type: {row.type}")
                        print(f"attachmentId: {row.attachmentId}")
                        print(f"text: {row.text}")
                        print("-" * 20)
                        
                        # If we found an attachment table earlier, try to query it here? 
                        # We'll do it in a generic way if 'chats.attachment' exists
                        if row.attachmentId:
                            try:
                                att_query = text(f'SELECT * FROM chats.attachment WHERE id = \'{row.attachmentId}\'')
                                att_res = conn.execute(att_query).fetchone()
                                if att_res:
                                    print(f"Attachment Data: {att_res}")
                            except Exception as ex:
                                print(f"Could not query chats.attachment: {ex}")

        except Exception as e:
            print(f"Error querying chat 18345: {e}")
            
if __name__ == "__main__":
    analyze_messages()

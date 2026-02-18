import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SOURCE_DB_URI = os.getenv("SOURCE_DB_URI")
if not SOURCE_DB_URI:
    print("SOURCE_DB_URI not found in environment variables")
    sys.exit(1)

# Base URL for images
BASE_URL = "https://towebs.clientes.flamachat.com/file/"

def fetch_chat_images(chat_id):
    engine = create_engine(SOURCE_DB_URI)
    
    with engine.connect() as conn:
        # Query to get messages with attachments including role/author info if available
        # Adjusting query based on previous analysis of 'chats.message' and 'core.attachment'
        query = text("""
            SELECT 
                m.id AS message_id,
                m.type,
                m.metadata,
                m."attachmentId",
                m."createdAt",
                a.path AS attachment_path,
                m.author
            FROM chats.message m
            LEFT JOIN core.attachment a ON m."attachmentId" = a.id
            WHERE m."chatId" = :chat_id
              AND (m."attachmentId" IS NOT NULL OR m.type = 'image')
            ORDER BY m."createdAt" ASC
        """)
        
        try:
            result = conn.execute(query, {"chat_id": chat_id})
            rows = result.fetchall()
            
            if not rows:
                print("RESULT: NO_IMAGES_FOUND")
                return

            print(f"Found {len(rows)} potential image messages for Chat ID {chat_id}")
            
            for index, row in enumerate(rows, start=1):
                # Determine Role/Author
                role = "Unknown"
                if row.author:
                    # Author is a JSON/dict
                    if isinstance(row.author, dict):
                         role = row.author.get('pushName', 'Unknown') or row.author.get('id', 'Unknown')
                    else:
                        role = str(row.author)
                
                # Check for path in attachment table
                image_url = None
                if row.attachment_path:
                    # clean path: remove leading slash if present to avoid double slash with base url
                    clean_path = row.attachment_path.lstrip('/')
                    image_url = f"{BASE_URL}{clean_path}"
                else:
                    image_url = "[IMAGE_BUT_NO_ATTACHMENT_PATH_FOUND]"

                print(f"[{index}] [{role}]: {image_url}")

        except Exception as e:
            print(f"Error fetching images: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_chat_images.py <chat_id>")
        sys.exit(1)
    
    chat_id_arg = sys.argv[1]
    fetch_chat_images(chat_id_arg)

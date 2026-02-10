from backend.database import SourceSession, init_db
from backend.models import Chat, Message
from sqlalchemy import select
import json

init_db()
session = SourceSession()

# Get a few messages to inspect author field
stmt = select(Message).limit(5)
messages = session.execute(stmt).scalars().all()

print("--- Message Author Data ---")
for m in messages:
    print(f"ID: {m.id}, Text: {m.text[:20]}..., Author Type: {type(m.author)}, Author: {m.author}")

# Get chat metadata
stmt = select(Chat).limit(1)
chat = session.execute(stmt).scalars().first()
print("\n--- Chat Metadata ---")
print(f"ID: {chat.id}, Metadata Type: {type(chat.msg_metadata)}, Metadata: {chat.msg_metadata}")

session.close()

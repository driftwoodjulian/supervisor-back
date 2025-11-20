from entity.chat import Chat
from datetime import datetime



def chat_duration(created_at_str, closed_at_str):
    fmt = "%Y-%m-%d %H:%M:%S.%f"  # matches "Tue, 16 Sep 2025 08:25:31 GMT"
    created_at = datetime.strptime(created_at_str, fmt)
    closed_at = datetime.strptime(closed_at_str, fmt)

    duration = closed_at - created_at
    return duration

def get_current_chats():
    chats = Chat.query.filter(Chat.closedAt.is_(None)).all()
    return chats

def get_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id).first()
    duration = "none yet"
    if chat.closedAt != None:
        
        duration = chat_duration(str(chat.createdAt) ,str(chat.closedAt))

    info = {
        "chat_id": chat.id,
        "displayname": chat.displayName,
        "closed_at": chat.closedAt,
        "created_at": chat.createdAt,
        "custumer_metadata": chat.msg_metadata,
        "chat_duration": str(duration)
    }
    return info

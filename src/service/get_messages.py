from entity.message import Message

def get_messages(chat_id):
    messages = Message.query.filter_by(chatId=chat_id).order_by(Message.createdAt).all()
    result = []
    

    for message in messages:

        role = ""
        if isinstance(message.author, dict) == True:
            role= "support operator"
        if isinstance(message.author, str):
            role="customer"

        result.append(
            {
                "id": str(message.id),
                "chatId": message.chatId,
                "text": message.text,
                "createdAt": message.createdAt.isoformat(),
                "author": message.author,
                "role": role
            }
        )

    return {"conversation": result}

def convert_to_harmony(full_chat, rating="unrated"):
    chat_info = full_chat.get("chat_and_customer_info", {})
    cust_info = chat_info.get("custumer_metadata", {})
    conversation = full_chat.get("conversation", [])
    
    messages = []
    for msg in conversation:
        role = "support agent" if msg.get("role") == "support operator" else "client"
        messages.append({
            "role": role,
            "content": (msg.get("text") or "").strip()
        })
    

    return {"messages": messages}


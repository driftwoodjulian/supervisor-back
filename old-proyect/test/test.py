import json

def convert_to_harmony(full_chat, rating="unrated"):
    chat_info = full_chat.get("chat_and_customer_info", {})
    cust_info = chat_info.get("custumer_metadata", {})
    conversation = full_chat.get("conversation", [])
    
    messages = []
    for msg in conversation:
        role = "user" if msg.get("role") == "support operator" else "client"
        messages.append({
            "role": role,
            "content": msg.get("text", "").strip()
        })
    
    metadata = {
        "chat_id": chat_info.get("chat_id"),
        "chat_duration": chat_info.get("chat_duration"),
        "created_at": chat_info.get("created_at"),
        "closed_at": chat_info.get("closed_at"),
        "agent_name": (
            conversation[0]["author"]["pushName"]
            if conversation and isinstance(conversation[0].get("author"), dict)
            else None
        ),
        "customer_name": cust_info.get("name"),
        "domain": cust_info.get("dominio"),
        "area": cust_info.get("area"),
        "plan": cust_info.get("plan"),
        "estado": cust_info.get("estado"),
        "proximo_pago": cust_info.get("proximo_pago"),
        "servidor": cust_info.get("servidor"),
        "satisfaction": rating
    }

    return {"messages": messages, "metadata": metadata}


# Example usage
if __name__ == "__main__":
    with open("chat_example_full.json") as f:
        chat = json.load(f)

    harmony_data = convert_to_harmony(chat)
    print(json.dumps(harmony_data, ensure_ascii=False, indent=2))


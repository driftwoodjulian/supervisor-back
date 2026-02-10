from crypt import methods
from flask import Blueprint, jsonify, request
from sqlalchemy import null
from service.get_chat import get_chat
from service.get_messages import get_messages
from decorators.auth import preauth


conversation_bp = Blueprint("conversation_controller", __name__)



def convert_to_harmony(full_chat, rating="unrated"):
    chat_info = full_chat.get("chat_and_customer_info", {})
    cust_info = chat_info.get("custumer_metadata", {})
    conversation = full_chat.get("conversation", [])
    
    messages = []
    for msg in conversation:
        role = "support agent" if msg.get("role") == "support operator" else "client"
        if msg.get("text", '') == None:
            messages.append({
                "role": role,
                "content": "image"
            })
        else:
            messages.append({
                "role": role,
            "content": (msg.get("text") or "").strip()
            })

    #we are not using the metadata for now
    '''
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
    '''
    return {"messages": messages}



@conversation_bp.route("conversation/<int:chat_id>", methods=["GET"])
@preauth
def conversation_controller(chat_id):
    messages = get_messages(chat_id)
    chat = get_chat(chat_id)

    info = {
        "conversation": messages["conversation"],
        "chat_and_customer_info": chat
    }

    data=convert_to_harmony(full_chat=info)

    return jsonify(data), 200


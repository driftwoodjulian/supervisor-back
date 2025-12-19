from flask import Blueprint, jsonify, request
from sqlalchemy.engine import characteristics
from service.get_chat import get_current_chats
from decorators.auth import preauth


current_chats_bp = Blueprint("current_chats_controller", __name__)


@current_chats_bp.route("/get_current", methods=["GET"])
@preauth
def current_chats_controller():
    response = None
    try:
        current_chat_ids = []
        chats = get_current_chats()
        for chat in chats:
            current_chat_ids.append(chat.id)
        if len(current_chat_ids) == 0:
            response = jsonify({"error": "no chats currently"}), 200    
        response = jsonify({"chat_ids": current_chat_ids }), 200
    except Exception as e:
        print(e)
        response = jsonify({"error": "error with the current chats query controller"}), 500
    return response



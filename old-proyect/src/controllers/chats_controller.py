from crypt import methods
import json
from entity.chat import Chat
from service.get_chat import get_chat
from flask import Blueprint, jsonify, request
from decorators.auth import preauth


chats_bp = Blueprint('chat_controller', __name__)

@chats_bp.route("chats/<int:chat_id>", methods=["GET"])
@preauth
def chat_controller(chat_id):
    return jsonify(get_chat(chat_id)), 200

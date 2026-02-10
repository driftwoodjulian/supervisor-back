from flask import Blueprint, jsonify, request
from service.get_messages import get_messages
from crypt import methods
from decorators.auth import preauth


messages_bp = Blueprint('messages_controller', __name__)
@messages_bp.route('/messages/<int:chat_id>', methods=["GET"])
@preauth
def get_messages_route(chat_id):
    return jsonify(get_messages(chat_id)), 200



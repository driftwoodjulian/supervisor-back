
from flask import request, jsonify, Blueprint
from datetime import datetime, timedelta
import bcrypt
from entities.user import User
from utils.jwt.jwt import create_access_token

hashed = bcrypt.hashpw("seremospobresperoporlomenosnosomosicardi".encode("utf-8"), bcrypt.gensalt())
print(hashed.decode())






login_bp = Blueprint('login_controller', __name__)
@login_bp.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Missing credentials"}), 401

    token = create_access_token(user.username, user.role)
    return jsonify({"jwt": token}),200

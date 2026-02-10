from flask import Blueprint, Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import jwt
import bcrypt
from entities.user import User
from utils.jwt.jwt import verify_token

check_bp =Blueprint("check_jwt", __name__)

@check_bp.route("/check", methods=["GET"])

def check():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]

    try:
        payload = verify_token(token)
        print(payload)
        username = payload.get("sub")
        role = payload.get("role")
        
    except Exception:
        return jsonify({"error": "Invalid token"}), 401

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"username": username, "role": role, "status": "valid"}),200
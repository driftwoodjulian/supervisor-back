from functools import wraps
from flask import request, jsonify
from entities.user import User
from utils.jwt.jwt import verify_token
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def preauth(required_role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid token"}), 401

            token = auth_header.split(" ")[1]

            try:
                payload = verify_token(token)
                username = payload.get("sub")
                role = payload.get("role")

            except ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except InvalidTokenError:
                return jsonify({"error": "Token has expired"}), 401
            


            # check if user exists
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            # check role if required
            if required_role and role != required_role:
                return jsonify({"error": "Forbidden, requires role: " + required_role}), 403

            # inject user into request context
            request.user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator

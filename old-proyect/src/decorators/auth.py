import os
import requests
from flask import request, jsonify, current_app
from functools import wraps

def check_token_validity(token):
    """
    Verifies the token against the auth service.
    Returns True if valid, False otherwise.
    """
    # Load AUTH_SERVICE_URL from app config or env, defaulting to localhost
    auth_service_url = os.environ.get("AUTH_SERVICE_URL", "http://localhost:5000/auth/check")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(auth_service_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"Auth service error: {e}")
        return False

def preauth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token format"}), 401
        
        token = auth_header.split(" ")[1]
        
        if not check_token_validity(token):
            return jsonify({"error": "Unauthorized: Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

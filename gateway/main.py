from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# CORS(app) # Disable flask_cors to prevent conflicts

BACKEND_URL = f"http://{os.getenv('CURRENT_HOST_IP')}:{os.getenv('BACKEND_PORT')}"

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    
    try:
        resp = requests.request(
            method=request.method,
            url=f"{BACKEND_URL}/api/{path}",
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False)
            
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return (resp.content, resp.status_code, headers)
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Backend unavailble"}), 502

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    return response

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "gateway_ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('GATEWAY_PORT', 5000)))

import json
from flask import Blueprint, request, jsonify
from utils.checkFileData import checkFileData
from ssh.load import load
from controllers.preauth import preauth
load_bp = Blueprint('load_controller', __name__)

@load_bp.route('/carga', methods=['POST'])
@preauth()
def carga_route():
    data = request.get_json()
    response = None
    if not data:
        response = jsonify({"error": "No JSON data provided"}),400
    else:
        user = data.get('user', '').strip()
        srv = data.get('srv', '').strip()

        if not user or not srv:
            response = jsonify({"error": "Missing fields"}), 400
        else:
            if not checkFileData(srv=user, filepath='/home/julian/miamivice/web/users.txt'):
                response = jsonify({"error": "not a user"}),400
            else:
                if not checkFileData(srv=srv, filepath="/home/julian/miamivice/bot/src/srv.txt"):
                    response = jsonify({"error": "not a server"}),400
                else:
                    
                    response = load(srv)
    return response
                




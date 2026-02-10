import json
from flask import Blueprint, request, jsonify
from utils.checkFileData import checkFileData
from ssh.hermes import hermes
from controllers.adminpreauth import adminpreauth

hermes_bp= Blueprint('hermes_controller', __name__)

@hermes_bp.route('/hermes', methods=['POST'])
@adminpreauth()
def hermes_controller():
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
                    
                    response = hermes(srv)
    return response
                
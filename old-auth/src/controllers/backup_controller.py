import json
from flask import Blueprint, request, jsonify
from paramiko import client
from utils.checkFileData import checkFileData
from controllers.preauth import preauth
from ssh.backup_checker import backup_checker



backup_bp = Blueprint('backup_controller', __name__)

@backup_bp.route("/backup", methods=['POST'])
@preauth()
def backup():

    data = request.get_json()
    print(data)
    response = None
    if not data:
        response = jsonify({"error": "No JSON data provided"}),400
    else:
        user = data.get('user', '').strip()
        srv = data.get('srv', '').strip()
        client = data.get('client', '').strip()
        print(user, srv, client)


       
        if not user or not srv or not client:
            response = jsonify({"error": "Missing fields"}), 400
        else:
            if not checkFileData(srv=user, filepath='/home/julian/miamivice/web/users.txt'):
                response = jsonify({"error": "not a user"}),400
            else:
                if not checkFileData(srv=srv, filepath="/home/julian/miamivice/bot/src/srv.txt"):
                    response = jsonify({"error": "not a server"}),400
                else:
                    response = backup_checker(srv=srv, client=client)
    return response
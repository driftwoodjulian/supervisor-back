import json
from flask import Blueprint, request, jsonify
from utils.checkFileData import checkFileData
from ssh.unblock_ip import unblock
from controllers.preauth import preauth
unblock_bp = Blueprint('unblock_controller', __name__)

@unblock_bp.route('/unblock', methods=['POST'])
@preauth()
def ipcheck():
    data = request.get_json()
    print(data)
    response = None
    if not data:
        response = jsonify({"error": "No JSON data provided"}),400
    else:
        user = data.get('username', '').strip()
        srv = data.get('srv', '').strip()
        ip =  data.get('ip', '').strip()
        print(user, srv, ip + "0000000000000s")

        
        if not user or not srv or not ip:
            response = jsonify({"error": "Missing fields----"}), 500
        else:
            if not checkFileData(srv=user, filepath='/home/julian/miamivice/web/users.txt'):
                response = jsonify({"error": "not a user"})
            else:
                if not checkFileData(srv=srv, filepath="/home/julian/miamivice/bot/src/srv.txt"):
                    response = jsonify({"error": "not a server"}),400
                else:
                    if ('/' in ip):
                        response = jsonify({"error": "Caracteres prohibidos en la ip"}),400
                    else:
                        if ("127.0.0." in ip) or ("172.168.1" in ip) or ("192.168.1" in ip) or ("0.0.0.0" in ip):
                            response = jsonify({"error":"IPs prohibidas"}),400
                        else:
                            print("Un blocking")
                            response = unblock(srv=srv, ip=ip)
    print(response)
    return response

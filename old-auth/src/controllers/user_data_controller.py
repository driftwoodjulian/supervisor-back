import json
from flask import Blueprint, request, jsonify
from ssh.password_change import change_password
from utils.checkFileData import checkFileData
from utils.email_sender import email_sender
from controllers.preauth import preauth

user_data_bp= Blueprint('user_data_controller', __name__)



@user_data_bp.route('/new_data', methods=['POST'])
@preauth()
def user_data_controller():

    data = request.get_json()
    print(data)
    response = None
    if not data:
        response = jsonify({"error": "No JSON data provided"}),400
    else:
        user = data.get('username', '').strip()
        srv = data.get('srv', '').strip()
        password =  data.get('password', '').strip()
        username = data.get('client', '').strip()
        mail = data.get('mail','').strip()
        if not user or not srv or not password or not username:
            response = jsonify({"error": "Missing fields"}), 500
        else:
            if not checkFileData(srv=user, filepath='/home/julian/miamivice/web/users.txt'):
                response = jsonify({"error": "not a user"})
            else:
                if not checkFileData(srv=srv, filepath="/home/julian/miamivice/bot/src/srv.txt"):
                    response = jsonify({"error": "not a server"}),400
                else:
                    if not checkFileData(srv=srv, filepath="/home/julian/miamivice/web/directadmin.txt"):
                        response = jsonify({"error": "Servidor no valido para cambio de claves"}),400
                    else:
                        if ("root" in username) or ("admin" in username):
                            response = jsonify({"error":"username prohibido"}),400
                        else:
                            try:
                                change_password(username=username , password=password, server=srv)
                                try:
                                    email_sender(reciever=mail, srv=srv , password=password, username=username)
                                    response = ({"data": "el correo se envio con exito"})
                                except Exception as e:
                                    print(e)
                                    response = jsonify({"error":"error al enviar el correo"})
                            except Exception as e:
                                print(e)
                                response=  jsonify({"error": "error cambiando la clave"})


    return response



    

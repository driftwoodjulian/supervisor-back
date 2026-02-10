import paramiko
from flask import jsonify


def backup_checker(srv, client):
    response = None
    hostname = srv+".toservers.com"
    username = "root"


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    com= "ls -lath /dagon | grep cpmove-{}.tar".format(client)


    
    try:
        ssh.connect(hostname, username=username)
        stdin, stdout, stderr = ssh.exec_command(com)
        output= stdout.read().decode().replace("\n" , "")
        error = stderr.read().decode()
        response= jsonify({"data": str(output)}), 200

    except Exception as e:
        print(e)
        response = jsonify({"error": "error ejecutando query"}), 500
    
    ssh.close()


    return response

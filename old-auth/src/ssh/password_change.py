import paramiko
from flask import jsonify
from sqlalchemy import outerjoin

def change_password(username, password, server):
    response = None

    hostname = server+".toservers.com"
    user= "root"    


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    com= "python3 /root/miamivice/change_pass.py {} {}".format(str(username), str(password))

    ssh.connect(hostname, username=user)
    stdin, stdout, stderr = ssh.exec_command(com)

    output= stdout.read().decode().replace("\n" , "")
    error = stderr.read().decode()

    print("Output:")
    print(output)
    print("error:")
    print(error)

    response= jsonify({"data": output}),200
    

    response = jsonify({"error": "error ejecutando el cambio"}),500

    ssh.close()


    return response


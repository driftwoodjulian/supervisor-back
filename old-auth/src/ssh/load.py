import paramiko
from flask import jsonify

def load(server):
    response = None

    hostname = server+".toservers.com"
    username = "root"


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    com= f"uptime"

    try:
        ssh.connect(hostname, username=username)
        stdin, stdout, stderr = ssh.exec_command(com)

        output= stdout.read().decode().replace("\n" , "")
        error = stderr.read().decode()

        print("Output:")
        print(output.split("e:"))
        print("error:")
        print(error)
        new_out = output.split("e:")
        response= jsonify({"data": str(new_out[1])}),200
        

    except Exception as e:
        print(e)
        response = jsonify({"error": "error ejecutando query"}),500
    
    ssh.close()


    return response



    
import paramiko
from flask import jsonify
import ast


def hermes(server):
    response = None

    hostname = server+".toservers.com"
    username = "root"


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    com= "python3 /root/miamivice/kingSlayer.py"

    try:
        ssh.connect(hostname, username=username)
        stdin, stdout, stderr = ssh.exec_command(com)

        output= stdout.read().decode().replace("\n" , "")
        error = stderr.read().decode()
        '''
        print("Output:")
        print(output)
        print("error:")
        print(error)'''

        if output:
            new_out = ast.literal_eval(output)
            for data in new_out:
                print(data)
            response= jsonify({"data": new_out}),200
        else:
            response= jsonify({"data": "nope"}), 500
        

    except Exception as e:
        print(e)
        response = jsonify({"error": "error ejecutando query"})
    
    ssh.close()


    return response

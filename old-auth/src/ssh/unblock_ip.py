
import paramiko
from flask import jsonify



def unblock(srv, ip):
    response = None
    hostname = srv+".toservers.com"
    username = "root"
    has_csf = False
    print("server: "+ srv)
    print("ip: " + ip)
    command = "csf -dr {}".format(ip.strip())
    print(command)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        response = jsonify({
                            "data": {
                                "message": "Se ejecutó csf -dr",
                                "csf_output": output,
                                "csf_error": error
                            }
                        }), 200
    except Exception as e:
        print(e)
        response = jsonify({"error": "error de csf"}), 500
    finally:
        ssh.close()
    return response
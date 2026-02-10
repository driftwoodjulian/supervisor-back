
import paramiko
from flask import jsonify

def ipchecker(srv, ip):
    response = None
    hostname = srv+".toservers.com"
    username = "root"
    has_csf = False
    command1 = "csf"
    print("server: "+ srv)
    print("ip: " + ip)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


    try:
        ssh.connect(hostname, username=username)
        stdin, stdout, stderr = ssh.exec_command(command1)

        output = stdout.read().decode().replace("\n" , "")
        error = stderr.read().decode()
        print("OUT: "+output)
        print("ERR: " + error)

        if output:
            # Ejecutar greps por separado
            csf_deny_grep_cmd = "grep -E '^{}( |$)' /etc/csf/csf.deny".format(ip)
            lfd_log_grep_cmd = "grep ' {} ' /var/log/lfd.log".format(ip)
            csf_deny_out = ""
            lfd_log_out = ""
            try:
                print(csf_deny_grep_cmd)
                stdin_csf, stdout_csf, stderr_csf = ssh.exec_command(csf_deny_grep_cmd)
                csf_deny_out = stdout_csf.read().decode()
                csf_deny_err = stderr_csf.read().decode()
                print(lfd_log_grep_cmd)
                stdin_lfd, stdout_lfd, stderr_lfd = ssh.exec_command(lfd_log_grep_cmd)
                lfd_log_out = stdout_lfd.read().decode()
                lfd_log_err = stderr_lfd.read().decode()
            except Exception as e:
                print(e)
                print("error doing grep")

            if "cPanel" in output or "DirectAdmin" in output:
                print("Tien csf")
                # Si se encontró en csf.deny, ejecutar csf -d y devolver ambos logs
                if csf_deny_out:
                    command2 = "csf -dr {}".format(ip.strip())
                    print(command2)
                    try:
                        response = jsonify({
                            "data": {
                                "message": "Encontrada en csf.deny y se puede ejecutar un csf -dr",
                                "csf_deny_log": csf_deny_out,
                                "lfd_log": lfd_log_out,

                            }
                        }), 200
                    except Exception as e:
                        print(e)
                        response = jsonify({"error": "error de csf"}), 500
                else:
                    # No se encontró en csf.deny → no estaba bloqueada
                    response = jsonify({
                        "data": {
                            "message": "La ip no estaba bloqueda",
                            "csf_deny_log": csf_deny_out,
                            "lfd_log": lfd_log_out
                        }
                    }), 200
            else:
                print("uh tiene csf pero no se que paso")
                print(output)
                response = jsonify({"error": "ERROR CON EL FIREWALL"}), 500

        elif error and "not found" in error:
            print("Tiene iptables")
            command2 = "iptables -S | grep {} | head -n 1 |grep DROP".format(ip.strip())
            print(command2)
            stdin2, stdout2, stderr2 = ssh.exec_command(command2)
            output2 = stdout2.read().decode()
            error2 =  stderr2.read().decode()
            print("out:" + output2)
            if not output2 and not error2:
                print("iptables no la esta bloqueando")
                response = jsonify({"data":"Esta ip no esta siendo bloqueada"}), 200
            elif output2:
                print("Se encontro match en iptables " + output2)
                command3 = "iptables -I INPUT -s {} -j ACCEPT".format(ip.strip())
                stdin3 , stdout3, stderr3 = ssh.exec_command(command3)
                output3 = stdout3.read().decode()
                error3 = stdout3.read().decode()
                if output3 =="" and not output3:
                    response= jsonify({"data": "La ip fue desbloqueada exitosamente"}), 200
                elif error3:
                    response = jsonify({"error": "Hubo un error ejecutando el commando"}), 500
            else:
                response = jsonify({"error": "wtf"}),500
        else:
            response= jsonify({"error": "error ejecutando"}), 500
    except Exception as e:
        print(e)
        print("--------")
        response = jsonify({"error": "error ejecutando query"}),500
    finally:
        ssh.close()
    return response



import paramiko
from flask import jsonify

def whm_unblock(srv, ip):
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
            csf_allow_grep_cmd = "grep 'tcp|in|d=2087|s={}/32' /etc/csf/csf.allow".format(ip)

            csf_allow_out = ""

            try:
                print(csf_allow_grep_cmd)
                stdin_csf, stdout_csf, stderr_csf = ssh.exec_command(csf_allow_grep_cmd)
                csf_allow_out = stdout_csf.read().decode()
                csf_allow_err = stderr_csf.read().decode()

                #print("csf_allow_out: "+ csf_allow_out )
                #print("csf_allow_err"+ csf_allow_err)

            except Exception as e:
                print(e)
                print("error doing grep")

            if "cPanel" in output or "DirectAdmin" in output:
                print("Tien csf")
                
                if not csf_allow_out:
                    print(ip.strip())
                    command2 = "sed -i '35a tcp|in|d=2086|s={}/32' /etc/csf/csf.allow ; sed -i '35a tcp|in|d=2087|s={}/32' /etc/csf/csf.allow".format(ip.strip(), ip.strip())
                    print(command2)
                    try:
                        stdin2, stdout2, stderr2 = ssh.exec_command(command2)
                        output2 = stdout2.read().decode()
                        error2 =  stderr2.read().decode()
                        command3 = "systemctl restart csf"
                        stdin3, stderr3, stdout3 =  ssh.exec_command(command3)
                        if output2:
                            response = jsonify({
                                "data": {
                                    "message": "Se agrego al csf.allow",


                                }
                            }), 200
                        else:
                            response = jsonify({
                                "data":{
                                    "message": "Se agrego al csf.allow puede tardar en impactar"
                                }
                            })
                    except Exception as e:
                        print(e)
                        response = jsonify({"error": "error de csf"}), 500
                else:
                    # No se encontró en csf.deny → no estaba bloqueada
                    response = jsonify({
                        "data": {
                            "message": "La ip parece que ya estaba permitida para el whm",

                        }
                    }), 200
            else:
                print("uh tiene csf pero no se que paso")
                print(output)
                response = jsonify({"error": "ERROR CON EL FIREWALL"}), 500

        elif error and "not found" in error:
            print("Tiene iptables")
            command2 = "iptables -S | grep {} | grep 2087 | head -n 1".format(ip.strip())
            print(command2)
            stdin2, stdout2, stderr2 = ssh.exec_command(command2)
            output2 = stdout2.read().decode()
            error2 =  stderr2.read().decode()
            print("out:" + output2)
            if output2 and not error2:
                print("iptables no la esta bloqueando")
                response = jsonify({"data":{"message":"Esta ip parece ya esta authorizada en whm"}}), 200
            elif not output2:
                print("No encontro match de whm en iptables ")
                command3 = "iptables -I INPUT -s {} -p tcp -m tcp --dport 2087 -j ACCEPT ; iptables -I INPUT -s {} -p tcp -m tcp --dport 2087 -j ACCEPT".format(ip.strip(), ip.strip())
                stdin3 , stdout3, stderr3 = ssh.exec_command(command3)
                output3 = stdout3.read().decode()
                error3 = stdout3.read().decode()
                if output3 =="" and not output3:
                    response= jsonify({"data":{ "message":"La ip fue agregada al whm exitosamente"}}), 200
                elif error3:
                    response = jsonify({"error": "Hubo un error ejecutando el commando"}), 500
            else:
                response = jsonify({"error": "wtf"}),500
        else:
            response= jsonify({"error": "error ejecutando"}), 500
    except Exception as e:
        print(e)
        print("--------")
        response = jsonify({"error": "error ejecutando query whm"}),500
    finally:
        ssh.close()
    return response
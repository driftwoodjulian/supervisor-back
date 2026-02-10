import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from werkzeug.wrappers import response




SMTP_SERVER = "webmail.towebs.com"  # e.g., smtp.office365.com
SMTP_PORT = 25  # Usually 587 for TLS
EMAIL = "soporte@towebs.com"
PASSWORD = "50port3Tow3B5"


def email_sender(reciever, username, srv, password):
    
    print("sending email to: " + reciever)

    TO_EMAIL = reciever
    SUBJECT = "Nuevos Datos de Ingreso a su Panel de Towebs"
    HTML_CONTENT = """
          <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 0;">
        <table align="center" width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); margin-top: 40px;">
            <tr>
                <td style="background-color: #00aff0; color: white; text-align: center; padding: 20px 0; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                    <h1 style="margin: 0;">Towebs</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 30px;">
                    <p style="font-size: 16px; color: #333;">Hola,</p>
                    <p style="font-size: 15px; color: #333;">
                        Te enviamos tus nuevos datos de acceso al panel de <b>Towebs</b>:
                    </p>
                    <table width="100%" cellpadding="8" style="background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; margin: 15px 0;">
                        <tr>
                            <td width="30%" style="font-weight: bold;">Usuario:</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td width="30%" style="font-weight: bold;">Nueva Contraseña:</td>
                            <td>{}</td>
                        </tr>
                    </table>

                    <p style="font-size: 15px; color: #333;">
                        Puedes ingresar al panel desde el siguiente enlace:
                    </p>
                    <p style="text-align: center; margin: 25px 0;">
                        <a href="{}" style="background-color: #00aff0; color: white; text-decoration: none; padding: 12px 25px; border-radius: 6px; font-weight: bold;">
                            Ir al Panel
                        </a>
                    </p>

                    <p style="font-size: 14px; color: #666; text-align: center;">
                        Si tienes dudas o necesitas asistencia, visita nuestro sitio web:
                        <br>
                        <a href="https://towebs.com" style="color: #2e6c80; text-decoration: none;">towebs.com</a>
                    </p>
                </td>
            </tr>
            <tr>
                <td style="background-color: #f0f0f0; text-align: center; padding: 10px; font-size: 12px; color: #777; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                    © TOWEBS - Todos los derechos reservados
                </td>
            </tr>
        </table>
    </body>
    </html>
       """.format(str(username), str(password), "https://"+str(srv)+".toservers.com:2222/evo/login")

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = SUBJECT

    msg.attach(MIMEText(HTML_CONTENT, "html"))
    try:
    # Example: Gmail SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            print(f"✅ Email sent to {TO_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")



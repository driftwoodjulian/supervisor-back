from curses import A_ALTCHARSET
from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
from sockets.sock_extention import sock
from controllers.satisfaction_controller import satisfaction_bp
from entity.session import db
from service.get_messages import get_messages
from controllers.messages_controller import messages_bp
from controllers.chats_controller import chats_bp
from controllers.conversation_controller import conversation_bp
from controllers.current_chats_controller import current_chats_bp
from sockets.satisfaction_sock import satisfaction_ws , query_scores
import threading


def create_app():
    app = Flask(__name__)
    sock.init_app(app)
    CORS(app, resources={r"/*":{"origins":"*"}})

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/towebs"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(messages_bp, url_prefix="/api")
    app.register_blueprint(chats_bp, url_prefix="/api")
    app.register_blueprint(conversation_bp, url_prefix="/api")
    app.register_blueprint(current_chats_bp, url_prefix="/api")
    app.register_blueprint(satisfaction_bp, url_prefix="/api")


    def start_background_job():
        # <-- context created INSIDE the thread
        with app.app_context():
            query_scores(app)

    # start thread AFTER everything is set up
    thread = threading.Thread(target=start_background_job, daemon=True)
    thread.start()
    
    return app
if __name__ == "__main__":
    app= create_app()

    app.run(debug=False,host="0.0.0.0", port=5050)
    
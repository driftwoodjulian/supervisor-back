from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
from ai import ai_bp

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}})


app.register_blueprint(ai_bp, url_prefix="/ai")

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=5040)
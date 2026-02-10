from flask import Flask
from flask_cors import CORS
from sqlalchemy.orm.attributes import register_attribute_impl
from controllers.ipcheck_controller import ipcheck_bp
from controllers.load_controller import load_bp
from controllers.backup_controller import backup_bp
from controllers.login_controller import login_bp
from controllers.check_jwt import check_bp
from controllers.authtest import authtest_bp
from controllers.hermes_contoller import hermes_bp
from controllers.unblock_controller import unblock_bp
from controllers.unblock_whm import unblock_whm_bp
from controllers.user_data_controller import user_data_bp
from entities.user import db
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


    # Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yolita1234@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

app.register_blueprint(load_bp, url_prefix='/api')
app.register_blueprint(ipcheck_bp, url_prefix='/api')
app.register_blueprint(backup_bp, url_prefix='/api')
app.register_blueprint(login_bp, url_prefix='/auth')
app.register_blueprint(check_bp, url_prefix='/auth')
app.register_blueprint(authtest_bp, url_prefix='/auth')
app.register_blueprint(hermes_bp, url_prefix='/api')
app.register_blueprint(unblock_bp, url_prefix='/unblock')
app.register_blueprint(unblock_whm_bp, url_prefix='/unblock')
app.register_blueprint(user_data_bp, url_prefix='/data')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

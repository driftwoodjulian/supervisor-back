from crypt import methods
from flask import request, jsonify, Blueprint
from functools import wraps
from controllers.preauth import preauth


authtest_bp =  Blueprint('authtest', __name__)

@authtest_bp.route("/authtest", methods=['GET'])
@preauth()
def authtest():
    return jsonify({
        "username": request.user.username,
        "role": request.user.role,
        "status": "valid"
    })

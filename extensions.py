from functools import wraps
from flask import request, g, jsonify, make_response
from models import User


class TokenAuth(object):
    def login_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies['token']

            g.user = User.verify_auth_token(token)

            if not g.user:
                return None

            return f(*args, **kwargs)
        return decorated

    def login_optional(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies['token']

            g.user = User.verify_auth_token(token)
            return f(*args, **kwargs)
        return decorated

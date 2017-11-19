from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from . import api
from .errors import unauthorized, forbidden
from ..models import AnonymousUser, User

auth = HTTPBasicAuth()


# 在访问所有api的路由之前必须先登录，同时禁止未认证账号访问
@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


# 使用密码或者令牌认证
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


# 登录之后获取密令
@api.route('/token')
def get_token():
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token':
        g.current_user.generate_auth_token(expiration=3600),
        'expiration':
        3600
    })


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

from flask import g
from . import api


# 获取某个用户
@api.route('/user/<int:id>')
def get_user(id):
    pass

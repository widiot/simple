from flask import render_template, url_for, abort
from . import main
from ..models import User


# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# 用户资料页面
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return render_template('user.html', user=user)

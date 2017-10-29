import datetime
from flask import redirect, url_for, flash, render_template
from flask_login import login_user, logout_user
from . import auth
from .forms import LoginForm, RegisterForm
from ..models import User
from .. import db


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.set_password(form.password.data)
        user.username = form.email.data
        user.avatar = 'default.jpg'
        user.register_date = datetime.datetime.now()

        db.session.add(user)
        db.session.commit()

    return redirect(url_for('register'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('账号或密码错误')
    return render_template('login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('成功退出登录')
    return redirect(url_for('auth.login'))

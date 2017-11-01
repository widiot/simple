import datetime
from flask import redirect, url_for, flash, render_template, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegisterForm
from ..models import User
from ..email import send_email
from .. import db


# 登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('账号或密码错误')

    return render_template('auth/login.html', current_user=None, form=form)


# 退出
@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('成功退出登录')


# 注册
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

        token = user.generate_confirmation_token()
        send_email(
            user.email, '认证你的邮箱', 'auth/email/confirm', user=user, token=token)

        flash('验证邮件已发送，请登录你的邮箱确认')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', current_user=None, form=form)


# 在邮件中点击的验证链接
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    # 如果已经认证，重定向到主页
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    # 验证令牌是否正确
    if current_user.confirm(token):
        flash('你的邮箱已经通过验证')
    else:
        flash('邮箱验证错误或过期')

    return redirect(url_for('main.index'))


# 过滤已经登录但是还未认证，请求的端点也不在auth中的用户，重定向到无权限页面
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        # 在每次请求前刷新上次访问时间
        current_user.ping()

        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':

            return redirect(url_for('auth.unconfirmed'))


# 如果是匿名用户或者已认证用户访问，则重定向到主页，否则到无权限页面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')


# 重新发送认证邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        '认证你的邮箱',
        'auth/email/confirm',
        user=current_user,
        token=token)
    flash('新的认证邮件已经发送到你的邮箱')

    return redirect(url_for('main.index'))

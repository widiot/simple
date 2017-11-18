from flask import redirect, url_for, flash, render_template, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from . import auth
from .forms import (LoginForm, RegisterForm, ChangePasswordForm,
                    ResetPasswordForm, SendVerification, ChangeEmailForm,
                    ChangeUsername, ChangeIntroduction)
from ..models import User
from ..email import send_email
from .. import db


# 过滤已经登录但是还未认证，请求的端点也不在auth中的用户，重定向到无权限页面
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


# 如果是匿名用户或者已认证用户，则重定向到主页，否则到无权限页面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')


# 登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)


# 退出
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# 注册
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 创建用户并提交到数据库
        user = User(
            email=form.email.data,
            username=form.email.data,
            register_date=datetime.utcnow())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # 发送验证邮件
        token = user.generate_confirmation_token()
        send_email(
            user.email, '认证你的邮箱', 'auth/email/confirm', user=user, token=token)
        flash('验证邮件已发送，请登录你的邮箱确认')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


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
        flash('邮箱验证错误或过期，请重试')
    return redirect(url_for('main.index'))


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


# 重置密码时发送认证邮件
@auth.route('/send-verification', methods=['GET', 'POST'])
def send_verification():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = SendVerification()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_reset_password_token()
        send_email(
            user.email,
            'Reset Your Password',
            'auth/email/reset_password',
            user=user,
            token=token,
            next=request.args.get('next'))
        flash('认证邮件已经发送，请登录你的邮箱进行确认')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password.html', send_verification_form=form)


# 重置密码
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.reset_password(token, form.password.data):
            flash('密码重置成功，请用新密码登录')
            return redirect(url_for('auth.login'))
        else:
            flash('令牌错误或过期，请重新发送验证邮件')
            return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password.html', reset_password_form=form)


# 更改设置
@auth.route('/settings/<option>', methods=['GET', 'POST'])
@login_required
def settings(option):
    # 设置中的表单
    change_username_form = ChangeUsername()
    change_introduction_form = ChangeIntroduction()
    change_password_form = ChangePasswordForm()
    change_email_form = ChangeEmailForm()

    # 如果是访问设置的主页，直接返回空表单，否则返回各个设置的表单。如果端点不存在，则返回404
    if option != 'index':
        if option == 'change-username':  # 修改昵称
            if change_username_form.validate_on_submit():
                current_user.username = change_username_form.username.data
                db.session.add(current_user._get_current_object())
                db.session.commit()
                flash('昵称修改成功')
            else:
                flash('昵称修改失败，请重试')
        elif option == 'change-introduction':  # 修改简介
            if change_introduction_form.validate_on_submit():
                current_user.introduction = change_introduction_form.introduction.data
                db.session.add(current_user._get_current_object())
                db.session.commit()
                flash('简介修改成功')
            else:
                flash('简介修改失败，请重试')
        elif option == 'change-password':  # 更改密码
            if change_password_form.validate_on_submit():
                current_user.set_password(change_password_form.password.data)
                db.session.add(current_user._get_current_object())
                db.session.commit()
                flash('密码更改成功')
            else:
                flash('密码更改失败，请重试')
        elif option == 'change-email':  # 更改邮箱
            if change_email_form.validate_on_submit():
                new_email = change_email_form.email.data
                token = current_user.generate_change_email_token(new_email)
                send_email(
                    new_email,
                    '验证你的邮箱',
                    'auth/email/change_email',
                    user=current_user,
                    token=token)
                flash('认证邮件已经发送，请登录你的邮箱进行确认')
            else:
                flash('邮箱更改失败，请重试')
        else:
            abort(404)

    # TextAreaField需要单独设置它的默认值
    change_introduction_form.introduction.data = current_user.introduction

    return render_template(
        'auth/settings.html',
        change_username_form=change_username_form,
        change_introduction_form=change_introduction_form,
        change_password_form=change_password_form,
        change_email_form=change_email_form)


# 更改邮箱
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('邮箱更改成功')
    else:
        flash('令牌错误或过期，邮箱更改失败')
    return redirect(url_for('main.index'))

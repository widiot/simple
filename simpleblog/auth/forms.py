from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..models import User


# 注册
class RegisterForm(FlaskForm):
    email = StringField(
        '邮箱',
        validators=[DataRequired(message='该行不能为空'),
                    Length(1, 64),
                    Email()])
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='该行不能为空'),
            Length(min=6, message='密码长度至少6位')
        ])
    repeat = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='该行不能为空'),
            EqualTo('password', message='密码不匹配')
        ])
    submit = SubmitField('注册Simple')

    # 检查邮箱是否已经存在
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册')


# 登录
class LoginForm(FlaskForm):
    email = StringField(
        '邮箱',
        validators=[DataRequired(message='该行不能为空'),
                    Length(1, 64),
                    Email()])
    password = PasswordField('密码', validators=[DataRequired(message='该行不能为空')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录Simple')

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # 表单合法性验证
        if not check_validate:
            return False

        # 按邮箱查找该用户
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('该邮箱未注册')
            return False

        # 检查密码
        if not user.check_password(self.password.data):
            self.password.errors.append('密码错误')
            return False

        return True


# 更改密码
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        '旧密码', validators=[DataRequired(message='该行不能为空')])
    password = PasswordField(
        '新密码',
        validators=[
            DataRequired(message='该行不能为空'),
            Length(min=6, message='密码长度至少6位')
        ])
    repeat = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='该行不能为空'),
            EqualTo('password', message='密码不匹配')
        ])
    submit = SubmitField('确认修改')

    def validate_old_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('原密码错误')

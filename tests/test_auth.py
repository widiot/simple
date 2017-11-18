import unittest
from flask import url_for
from simple import create_app, db
from simple.models import User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 测试注册和登录
    def test_register_and_login(self):
        # 注册一个用户
        response = self.client.post(
            url_for('auth.register'),
            data={
                'email': 'user@example.com',
                'password': '123456',
                'repeat': '123456'
            },
            follow_redirects=True)
        self.assertIn('验证邮件已发送，请登录你的邮箱确认', response.get_data(as_text=True))

        # 用该用户登录
        response = self.client.post(
            url_for('auth.login'),
            data={'email': 'user@example.com',
                  'password': '123456'},
            follow_redirects=True)
        self.assertIn('你现在还没有认证你的邮箱', response.get_data(as_text=True))

        # 验证邮箱
        user = User.query.filter_by(email='user@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(
            url_for('auth.confirm', token=token), follow_redirects=True)
        self.assertIn('你的邮箱已经通过验证', response.get_data(as_text=True))

        # 退出
        response = self.client.get(
            url_for('auth.logout'), follow_redirects=True)
        self.assertIn('登录', response.get_data(as_text=True))
        self.assertIn('注册', response.get_data(as_text=True))

    # 插入一个用户
    def insert_user(self):
        user = User()
        user.email = 'user@example.com'
        user.username = 'test'
        user.avatar = 'default.jpg'
        user.set_password('123456')
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return user

    # 测试重置密码
    def test_reset_password(self):
        user = self.insert_user()

        # 发送认证邮件
        response = self.client.post(
            url_for('auth.send_verification'),
            data={'email': 'user@example.com'},
            follow_redirects=True)
        self.assertIn('认证邮件已经发送，请登录你的邮箱进行确认', response.get_data(as_text=True))

        # 重置密码
        token = user.generate_reset_password_token()
        response = self.client.post(
            url_for('auth.reset_password', token='false token'),
            data={
                'email': 'user@example.com',
                'password': '654321',
                'repeat': '654321'
            },
            follow_redirects=True)
        self.assertIn('令牌错误或过期，请重新发送验证邮件', response.get_data(as_text=True))

        response = self.client.post(
            url_for('auth.reset_password', token=token),
            data={
                'email': 'user@example.com',
                'password': '654321',
                'repeat': '654321'
            },
            follow_redirects=True)
        self.assertIn('密码重置成功，请用新密码登录', response.get_data(as_text=True))

    # 测试个人设置
    def test_settings(self):
        user = self.insert_user()

        # 登录
        response = self.client.post(
            url_for('auth.login'),
            data={'email': 'user@example.com',
                  'password': '123456'},
            follow_redirects=True)
        self.assertIn('写博客', response.get_data(as_text=True))

        # 修改昵称
        response = self.client.post(
            url_for('auth.settings', option='change-username'),
            data={'username': 'test'},
            follow_redirects=True)
        self.assertIn('昵称修改成功', response.get_data(as_text=True))
        self.assertIn('test', response.get_data(as_text=True))

        # 修改简介
        response = self.client.post(
            url_for('auth.settings', option='change-introduction'),
            data={'introduction': 'This is my introduction'},
            follow_redirects=True)
        self.assertIn('简介修改成功', response.get_data(as_text=True))
        self.assertIn(
            'This is my introduction', response.get_data(as_text=True))

        # 更改密码
        response = self.client.post(
            url_for('auth.settings', option='change-password'),
            data={
                'old_password': '123456',
                'password': '654321',
                'repeat': '654321'
            },
            follow_redirects=True)
        self.assertIn('密码更改成功', response.get_data(as_text=True))

        response = self.client.post(
            url_for('auth.settings', option='change-password'),
            data={
                'old_password': '123456',
                'password': '654321',
                'repeat': '654321'
            },
            follow_redirects=True)
        self.assertIn('密码更改失败', response.get_data(as_text=True))
        self.assertIn('原密码错误', response.get_data(as_text=True))

        # 更改邮箱
        new_email = 'new@example.com'
        response = self.client.post(
            url_for('auth.settings', option='change-email'),
            data={
                'email': new_email,
                'password': '654321',
            },
        )
        self.assertIn('认证邮件已经发送，请登录你的邮箱进行确认', response.get_data(as_text=True))

        token = user.generate_change_email_token(new_email)
        response = self.client.get(
            url_for('auth.change_email', token=token), follow_redirects=True)
        self.assertIn('邮箱更改成功', response.get_data(as_text=True))

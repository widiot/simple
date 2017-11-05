import unittest
from flask import url_for
from simpleblog import create_app, db
from simpleblog.models import User


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
            })
        self.assertEqual(response.status_code, 302)

        # 用该用户登录
        response = self.client.post(
            url_for('auth.login'),
            data={'email': 'user@example.com',
                  'password': '123456'},
            follow_redirects=True)
        self.assertIn('你现在还没有认证你的邮箱', response.get_data(as_text=True))

        # 发送验证邮件
        user = User.query.filter_by(email='user@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(
            url_for('auth.confirm', token=token), follow_redirects=True)
        self.assertIn('你的邮箱已经通过验证', response.get_data(as_text=True))

        # 退出
        response = self.client.get(
            url_for('auth.logout'), follow_redirects=True)
        self.assertIn('你已经退出登录', response.get_data(as_text=True))

    # 测试个人设置
    def test_settings(self):
        # 插入一个用户
        user = User()
        user.email = 'user@example.com'
        user.username = 'test'
        user.avatar = 'default.jpg'
        user.set_password('123456')
        user.confirmed = True
        db.session.add(user)
        db.session.commit()

        # 登录
        response = response = self.client.post(
            url_for('auth.login'),
            data={'email': 'user@example.com',
                  'password': '123456'},
            follow_redirects=True)
        self.assertIn('Hello', response.get_data(as_text=True))

        # 更改密码
        response = self.client.post(
            url_for('auth.settings_option', option='change-password'),
            data={
                'old_password': '123456',
                'password': '654321',
                'repeat': '654321'
            },
            follow_redirects=True)
        self.assertIn('密码更改成功', response.get_data(as_text=True))

        response = self.client.post(
            url_for('auth.settings_option', option='change-password'),
            data={
                'old_password': '123456',
                'password': '654321',
                'repeat': '654321'
            },
            follow_redirects=True)
        self.assertIn('密码更改失败', response.get_data(as_text=True))
        self.assertIn('原密码错误', response.get_data(as_text=True))

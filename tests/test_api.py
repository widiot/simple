import unittest, json
from base64 import b64encode
from simple import create_app, db
from simple.models import Role


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 设置请求头
    def get_api_header(self, username, password):
        return {
            'Authorization':
            'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept':
            'application/json',
            'Content-Type':
            'application/json'
        }

    # 测试404
    def test_404(self):
        response = self.client.get(
            '/wrong/url', headers=self.get_api_header('email', 'password'))
        self.assertEqual(404, response.status_code)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual('not found', json_response['error'])

    # 测试没有认证的时候去访问
    def test_no_auth(self):
        response = self.client.get(
            '/api/v1.0/posts/', content_type='application/json')
        self.assertEqual(401, response.status_code)

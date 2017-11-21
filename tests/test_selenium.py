import unittest, threading
from selenium import webdriver
from simple import create_app, db
from simple.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
    client = None
    app_context = None

    @classmethod
    def setUpClass(cls):
        # 启动Chrome
        try:
            cls.client = webdriver.Chrome()
        except:
            pass

        # 如果无法启动浏览器，则跳过
        if cls.client:
            # 创建程序
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # 禁止日志，保持输出整洁
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            # 创建数据库，并插入一些数据
            db.create_all()
            Role.insert_roles()
            User.insert_test_user()

            # 在线程中启动服务器
            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 关闭服务器和浏览器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            # 销毁数据库
            db.drop_all()
            db.session.remove()

            # 删除上下文
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web brower not available')

    def tearDown(self):
        pass

    def test_home_page(self):
        # 进入首页
        self.client.get('http://localhost:5000/')
        self.assertIn('登录', self.client.page_source)

        # 进入登录页面
        self.client.find_element_by_link_text('登录').click()
        self.assertIn('登录Simple', self.client.page_source)

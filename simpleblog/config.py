import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SIMPLE_ADMIN = '984209543@qq.com'
    SIMPLE_MAIL_SUBJECT_PREFIX = '[Simple]'
    SIMPLE_MAIL_SENDER = 'Simple 管理员 <984209543@qq.com>'

    # 防止SQLAlchemy出现FSADeprecationWarning
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        root_dir, 'database-deve.db')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        root_dir, 'database-test.db')

    # raise RuntimeError('Application was not able to create a URL')
    SERVER_NAME = 'localhost:5000'


class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        root_dir, 'database-prod.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'product': ProductConfig,
}

import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    # 邮件配置
    SIMPLE_ADMIN = '984209543@qq.com'
    SIMPLE_MAIL_SUBJECT_PREFIX = '[Simple]'
    SIMPLE_MAIL_SENDER = 'Simple 管理员 <984209543@qq.com>'

    # 防止SQLAlchemy出现FSADeprecationWarning
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 每页的项目数
    SIMPLE_PER_PAGE = 5

    # 开启SQLAlchemy记录查询时间，并设置记录数据库缓慢查询时间的阀值
    SQLALCHEMY_RECORD_QUEIES = True
    SLOW_DB_QUERY_TIME = 0.5


class DevelopmentConfig(Config):
    DEBUG = True

    # sqlite数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        root_dir, 'database-deve.db')


class TestingConfig(Config):
    TESTING = True

    # 关闭CSRF保护，用于测试的时候方便提交表单
    WTF_CSRF_ENABLED = False

    # sqlite数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        root_dir, 'database-test.db')

    # raise RuntimeError('Application was not able to create a URL')
    SERVER_NAME = 'localhost:5000'


class ProductConfig(Config):
    # sqlite数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        root_dir, 'database-prod.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'product': ProductConfig,
}

import os

rootdir = os.path.pardir


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(rootdir, 'database-deve.db')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(rootdir, 'database-test.db')


class ProductConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(rootdir, 'database-prod.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'product': ProductConfig,
}

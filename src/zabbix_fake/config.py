# coding=utf-8
'''
the flask config file include dir would be used
'''


import os

basedir = os.path.abspath(os.path.dirname(__file__))
projectdir = os.path.abspath(os.path.dirname(basedir))
logdir = os.path.join(os.path.abspath(os.path.dirname(projectdir)), 'log')


class Config(object):
    SECRET_KEY = 'zMon&123'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    COLLECT_STATIC_ROOT = os.path.join(basedir, 'static')
    COLLECT_STORAGE = 'flask_collect.storage.file'
    CACHE_TYPE = 'simple'
    WTF_CSRF_METHODS = ['']

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@localhost:3306/alert'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class TestConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@localhost:3306/alert'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@localhost:3306/alert'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig,
}

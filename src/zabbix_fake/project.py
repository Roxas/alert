# coding=utf-8
'''
the project file, which define flask app and flask's thirdparty module
'''
from flask import Flask
from celery import Celery
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
'''
remove following comment when profile
'''
# from werkzeug.contrib.profiler import ProfilerMiddleware


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
    return app

app = create_app('development')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

celery.conf.update(app.config)

db = SQLAlchemy(app)

manager = Manager(app)

login_manager = LoginManager(app)

login_manager.login_view = 'monitor.login'

from alert import alert as alert_blueprint

app.register_blueprint(alert_blueprint)
# coding=utf-8
'''
the manage script which execute runserver and other commands
'''


from flask_migrate import Migrate, MigrateCommand
from project import app, db, manager

migrate = Migrate(app, db, compare_type=True)

manager.add_command('db', MigrateCommand)

from alert.models import *

if __name__ == '__main__':
    manager.run()

# coding=utf-8
'''
wsgi file which be used in uwsgi or gunicorn
'''


from project import app as application

if __name__ == "__main__":
    application.run()

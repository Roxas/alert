# coding=utf-8
'''
file desc: url API test cases, all test cases are dependent on some other service, including MySQL database
           redis server, admin account
'''

import os
import re
import unittest
import random
from project import app, db
from flask import json
from flask_testing import TestCase


# class LoginPlugin(object):
#     '''
#     class desc: all APIs are dependent on login, so package login plugin
#     '''
#     def __init__(self, flask_unittest):
#         self.unittest = flask_unittest
#         self.cookie = None

#     def create_app(self):
#         return app

#     def login(self):
#         login_html = self.unittest.client.get('/login.html').data
#         if not re.search('登录', login_html):
#             return False

#         params = {'username':'wjy', 'password':'wjy123'}
#         rep = self.unittest.client.post('/login.html', data=params, follow_redirects=True)
#         self.cookie = rep.headers['Set-Cookie']
#         result_data = rep.json

#         return True if result_data['status'] == 'ok' else False

#     def get_cookie(self):
#         return self.cookie

#     def logout(self):
#         return self.unittest.client.post('/logout')


# class BaseTest(TestCase):
#     '''
#     class desc: Abstract TestCase include basic create_app, login, logout feature
#     '''
#     is_login = None
#     cookie = None

#     def create_app(self):
#         self.login_plugin = LoginPlugin(self)
#         return self.login_plugin.create_app()

#     def setUp(self):
#         self.is_login = self.login_plugin.login()
#         self.cookie = self.login_plugin.get_cookie()

#     def tearDown(self):
#         self.login_plugin.logout()

class BaseTest(TestCase):
    '''
    class desc: Abstract TestCase include basic create_app
    '''
    cookie = None
    test_db = 'test_alert.db'

    def create_app(self):
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(self.test_db)
        return app

    def _remove_db_file(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def setUp(self):
        self._remove_db_file()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self._remove_db_file()


class EmailSMTPTest(BaseTest):
    '''
    class desc: test email SMTP setting
    '''
    def test_email_smtp_list_case(self):
        rep = self.client.get('/email/smtp/conf/list', headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

    def test_email_smtp_save_case(self):
        params = {'mail_host':'smtp.exmail.qq.com',
                  'mail_port':465,
                  'mail_subject':u'XX系统告警',
                  'account':'test_alert@163.com',
                  'password':'test_password',
                  'mail_from':'test_alert@163.com'}
        rep = self.client.post('/email/smtp/conf/save',
                               data=json.dumps(params),
                               content_type='application/json',
                               headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/email/smtp/conf/list', headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')
        self.assertDictEqual(rep.json['data'], params)


class EmailAlertLogTest(BaseTest):
    '''
    class desc: test fetch email alert log
    '''
    def test_email_log_case(self):
        rep = self.client.get('/email/logs.json', headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')


class TencentSMSTest(BaseTest):
    '''
    class desc: test tencent SMS conf
    '''
    def test_tencent_sms_conf_list_case(self):
        rep = self.client.get('/tencent/sms/conf/list', headers={'Cookie': self.cookie})
        self.assertEquals(rep.json['status'], 'ok')

    def test_tencent_sms_conf_case(self):
        params = {'app_id':1400049846,
                  'app_key':'dc931691afd60dd52cb41a52e5622011',
                  'templ_id':57708}
        rep = self.client.post('/tencent/sms/conf/save',
                               data=json.dumps(params),
                               content_type='application/json',
                               headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/tencent/sms/conf/list')
        self.assertEqual(rep.json['status'], 'ok')
        self.assertDictEqual(rep.json['data'], params)


class ReceiverTest(BaseTest):
    '''
    class desc: test sms receiver management
    '''
    def test_sms_receiver_list_case(self):
        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

    def test_sms_receiver_add_case(self):
        add_params = {'user_name':u'SMS测试用户1',
                      'user_phone':'15928444042',
                      'user_email_address':'aegiswing@163.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        added_receiver = rep.json['data'][-1]     # get last receiver
        self.assertEqual(added_receiver['user_name'], u'SMS测试用户1')
        self.assertEqual(added_receiver['user_phone'], '15928444042')
        self.assertEqual(added_receiver['user_email_address'], 'aegiswing@163.com')
        self.assertEqual(added_receiver['is_send_email'], True)
        self.assertEqual(added_receiver['is_send_sms'], True)

    def test_sms_receiver_remove_case(self):
        add_params = {'user_name':u'SMS测试用户2',
                      'user_phone':'15928444042',
                      'user_email_address':'aegiswing@163.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        added_receiver = rep.json['data'][-1]     # get last receiver
        self.assertEqual(added_receiver['user_name'], u'SMS测试用户2')
        self.assertEqual(added_receiver['user_phone'], '15928444042')

        remove_params = {'id':added_receiver['id']}
        rep = self.client.post('/receiver/remove',
                               data=json.dumps(remove_params),
                               content_type='application/json',
                               headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        is_exists = True if id in [r['id'] for r in rep.json['data']] else False
        self.assertEqual(is_exists, False)

    def test_sms_receiver_update_case(self):
        add_params = {'user_name':u'SMS测试用户3',
                      'user_phone':'18011585770',
                      'user_email_address':'306228331@qq.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        update_receiver = rep.json['data'][-1]     # get last receiver
        update_params = {'user_id':update_receiver['id'],
                         'user_name':u'SMS测试用户更新',
                         'user_phone':'18011585771',
                         'user_email_address':'306228331@163.com',
                         'is_send_email':False,
                         'is_send_sms':False}
        rep = self.client.post('/receiver/update',
                               data=json.dumps(update_params),
                               content_type='application/json',
                               headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        update_receiver = rep.json['data'][-1]
        self.assertEqual(update_receiver['user_name'], u'SMS测试用户更新')
        self.assertEqual(update_receiver['user_phone'], '18011585771')
        self.assertEqual(update_receiver['user_email_address'], '306228331@163.com')
        self.assertEqual(update_receiver['is_send_email'], False)
        self.assertEqual(update_receiver['is_send_sms'], False)

    def test_sms_notice_case(self):
        add_params = {'user_name':u'SMS测试用户1',
                      'user_phone':'18011585770',
                      'user_email_address':'306228331@qq.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        add_params = {'user_name':u'SMS测试用户2',
                      'user_phone':'15928444042',
                      'user_email_address':'aegiswing@163.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        user_ids = [u['id'] for u in rep.json['data']]

        params = {'user_list':user_ids, 'active':True}
        rep = self.client.post('/receiver/sms_notice',
                                data=json.dumps(params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        active_all = True
        for u in rep.json['data']:
            if u['is_send_sms'] == False:
                active_all = False
        self.assertEqual(active_all, True)

    def test_email_notice_case(self):
        add_params = {'user_name':u'SMS测试用户1',
                      'user_phone':'18011585770',
                      'user_email_address':'306228331@qq.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        add_params = {'user_name':u'SMS测试用户2',
                      'user_phone':'15928444042',
                      'user_email_address':'aegiswing@163.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        user_ids = [u['id'] for u in rep.json['data']]

        params = {'user_list':user_ids, 'active':False}
        rep = self.client.post('/receiver/email_notice',
                                data=json.dumps(params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        active_all = False
        for u in rep.json['data']:
            if u['is_send_email'] == True:
                active_all = True
        self.assertEqual(active_all, False)

    def test_email_test_case(self):
        add_params = {'user_name':u'SMS测试用户1',
                      'user_phone':'18011585770',
                      'user_email_address':'306228331@qq.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        test_receiver = rep.json['data'][-1]     # get last receiver

        params = {'user_id':test_receiver['id']}
        rep = self.client.post('/receiver/email_test',
                                data=json.dumps(params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

    def test_sms_test_case(self):
        params = {'app_id':1400049846,
                  'app_key':'dc931691afd60dd52cb41a52e5622011',
                  'templ_id':57708}
        rep = self.client.post('/tencent/sms/conf/save',
                               data=json.dumps(params),
                               content_type='application/json',
                               headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/tencent/sms/conf/list')
        self.assertEqual(rep.json['status'], 'ok')

        add_params = {'user_name':u'SMS测试用户1',
                      'user_phone':'18011585770',
                      'user_email_address':'306228331@qq.com',
                      'is_send_email':True,
                      'is_send_sms':True}
        rep = self.client.post('/receiver/add',
                                data=json.dumps(add_params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')

        rep = self.client.get('/receiver/list', headers={'Cookie': self.cookie})
        test_receiver = rep.json['data'][-1]     # get last receiver

        params = {'user_id':test_receiver['id']}
        rep = self.client.post('/receiver/sms_test',
                                data=json.dumps(params),
                                content_type='application/json',
                                headers={'Cookie': self.cookie})
        self.assertEqual(rep.json['status'], 'ok')


class SnmptrapSettingTest(BaseTest):
    '''
    class desc: test SNMP Trap settings
    '''
    def test_snmptrap_setting_list_case(self):
        '''
        to do
        '''
        pass

    def test_snmptrap_setting_save_case(self):
        '''
        to do
        '''
        pass


if __name__ == '__main__':
    unittest.main()

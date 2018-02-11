# coding=utf-8
'''
file desc: define view class or view function
'''


import datetime
import os
from flask import request, jsonify
from flask.views import MethodView
from project import app
from .models import *
from .utils import send_email, send_tencent_sms
from flask_login import login_required


class GeneralView(MethodView):
    '''
    class desc: self define base View,
    '''
    decorators = [login_required] if app.config['DEBUG'] == False else []


class EmailSMTPView(GeneralView):
    '''
    class desc: email smtp setting view class
    '''
    def get(self, action):
        actionfunc = {
            'list':self._list,
        }
        return actionfunc[action]()

    def post(self, action):
        actionfunc = {
            'save':self._save,
        }
        return actionfunc[action]()

    def _list(self):
        es = EmailSMTP.query.first()
        data = {
            'mail_host':'',
            'mail_port':'',
            'mail_subject':'',
            'account':'',
            'password':'',
            'mail_from':'',
        }
        if es:
            data.update({
                'mail_host':es.mail_host,
                'mail_port':es.mail_port,
                'mail_subject':es.mail_subject,
                'account':es.account,
                'password':es.password,
                'mail_from':es.mail_from,
            })

        res = {'status':'ok', 'data':data}
        return jsonify(res)

    def _save(self):
        req_data = request.get_json()
        mail_host = req_data.get('mail_host')
        mail_port = req_data.get('mail_port', 465)
        mail_subject = req_data.get('mail_subject')
        account = req_data.get('account')
        password = req_data.get('password')
        mail_from = req_data.get('mail_from')

        es = EmailSMTP.query.first()
        if not es:
            es = EmailSMTP(mail_host=mail_host,
                           mail_port=mail_port,
                           account=account,
                           password=password,
                           mail_subject=mail_subject,
                           mail_encoding='utf-8',
                           mail_from=mail_from)
            db.session.add(es)
        else:
            EmailSMTP.query.update({'mail_host':mail_host,
                                'mail_port':mail_port,
                                'account':account,
                                'password':password,
                                'mail_subject':mail_subject,
                                'mail_encoding':'utf-8',
                                'mail_from':mail_from,
                                })
        db.session.commit()

        res = {'status':'ok', 'msg':u'Email SMTP配置成功'}
        return jsonify(res)


class ReceiverView(GeneralView):
    '''
    class desc: Receiver management view
    '''
    def get(self, action):
        actionfunc = {
            'list':self._list,
        }
        return actionfunc[action]()

    def post(self, action):
        actionfunc = {
            'add':self._add,
            'update':self._update,
            'remove':self._remove,
            'sms_notice':self._sms_notice,
            'email_notice':self._email_notice,
            'sms_test':self._sms_test,
            'email_test':self._email_test,
        }
        return actionfunc[action]()

    def _list(self):
        qs = Receiver.query.all()

        data = []
        for q in qs:
            d = {}
            for attr in q._sa_instance_state.attrs.items():
                d[attr[0]] = getattr(q, attr[0], None)
            data.append(d)

        res = {'status':'ok', 'data':data}
        return jsonify(res)

    def _add(self):
        req_data = request.get_json()
        user_name = req_data.get('user_name')
        user_email_address = req_data.get('user_email_address')
        user_phone = req_data.get('user_phone')
        is_send_sms = req_data.get('is_send_sms')
        is_send_email = req_data.get('is_send_email')

        q = Receiver.query.filter_by(user_name=user_name).first()
        if q is not None:
            res = {'status':'failed', 'msg':u'用户{user}已经存在'.format(user=q.user_name)}
            return jsonify(res)

        db.session.add(Receiver(user_name=user_name,
                                user_email_address=user_email_address,
                                user_phone=user_phone,
                                is_send_sms=is_send_sms,
                                is_send_email=is_send_email))
        db.session.commit()

        res = {'status':'ok', 'msg':u'添加用户{user}成功'.format(user=user_name)}
        return jsonify(res)

    def _update(self):
        req_data = request.get_json()
        user_id = req_data.get('user_id')
        user_name = req_data.get('user_name')
        user_email_address = req_data.get('user_email_address')
        user_phone = req_data.get('user_phone')
        is_send_sms = req_data.get('is_send_sms')
        is_send_email = req_data.get('is_send_email')

        Receiver.query.filter_by(id=user_id).update({
                'user_name':user_name,
                'user_email_address':user_email_address,
                'user_phone':user_phone,
                'is_send_sms':is_send_sms,
                'is_send_email':is_send_email,
            })
        db.session.commit()

        res = {'status':'ok', 'msg':u'更新用户{user}成功'.format(user=user_name)}
        return jsonify(res)

    def _remove(self):
        req_data = request.get_json()
        user_id = req_data.get('user_id', 0)
        user_name = req_data.get('user_name', '')

        Receiver.query.filter_by(id=user_id).delete()

        db.session.commit()

        res = {'status':'ok', 'msg':u'移除用户{user}成功'.format(user=user_name)}
        return jsonify(res)

    def _sms_notice(self):
        req_data = request.get_json()
        user_list = req_data.get('user_list')
        active = req_data.get('active')

        Receiver.query.filter(Receiver.id.in_(user_list)).update({'is_send_sms':active},synchronize_session=False)
        db.session.commit()

        szmulti = u'批量' if len(user_list) > 1 else ''
        szactive = u'激活' if active else u'取消'
        msg = u'{}{}短信通知功能成功'.format(szmulti, szactive)
        res = {'status':'ok', 'msg':msg}
        return jsonify(res)

    def _email_notice(self):
        req_data = request.get_json()
        user_list = req_data.get('user_list')
        active = req_data.get('active')

        Receiver.query.filter(Receiver.id.in_(user_list)).update({'is_send_email':active},synchronize_session=False)
        db.session.commit()

        szmulti = u'批量' if len(user_list) > 1 else ''
        szactive = u'激活' if active else u'取消'
        msg = u'{}{}邮件通知功能成功'.format(szmulti, szactive)
        res = {'status':'ok', 'msg':msg}
        return jsonify(res)

    def _sms_test(self):
        req_data = request.get_json()
        user_id = req_data.get('user_id')

        es = TencentSMS.query.first()
        if not es:
            res = {'status':'failed', 'msg':u'请先配置腾讯SMS'}
            return jsonify(res)

        receiver_q = Receiver.query.filter_by(id=user_id).first()
        test_msg_content = u'测试短信发送功能'
        result, err = send_tencent_sms([receiver_q.user_phone], test_msg_content)
        if result:
            res = {'status':'ok', 'msg':u'测试短信发送功能'}
        else:
            res = {'status':'failed', 'msg':u'测试短信发送失败', 'reason':err}
        return jsonify(res)

    def _email_test(self):
        req_data = request.get_json()
        user_id = req_data.get('user_id')

        es = EmailSMTP.query.first()
        if not es:
            res = {'status':'failed', 'msg':u'请先配置邮件SMTP'}
            return jsonify(res)

        receiver_q = Receiver.query.filter_by(id=user_id).first()
        test_msg_content = u'测试邮件发送功能'
        result, err = send_email([receiver_q.user_email_address], test_msg_content)
        if result:
            res = {'status':'ok', 'msg':u'测试邮件发送成功'}
        else:
            res = {'status':'failed', 'msg':u'测试邮件发送失败', 'reason':err}
        return jsonify(res)


class EmailAlertLogView(GeneralView):
    def get(self):
        last_7day = datetime.datetime.today() - datetime.timedelta(days=7)

        qs = EmailAlertLog.query.filter(EmailAlertLog.created_datetime>last_7day).all()

        data = []
        for q in qs:
            d = {}
            for attr in q._sa_instance_state.attrs.items():
                d[attr[0]] = getattr(q, attr[0], None)
            data.append(d)

        res = {'status':'ok', 'data':data}
        return jsonify(res)


class SnmptrapSettingView(GeneralView):
    '''
    class desc: SNMPTRAP setting View
    '''
    def get(self, action):
        actionfunc = {
            'list':self._list,
        }
        return actionfunc[action]()

    def post(self, action):
        actionfunc = {
            'save':self._save,
        }
        return actionfunc[action]()

    def _list(self):
        sts = SnmptrapSetting.query.first()
        data = {
            'snmp_engine_id':'',
            'snmp_version':'',
            'snmptrap_host':'',
            'snmptrap_port':'',
            'notify_type':'',
            'safe_level':'',
            'user_name':'',
            'auth_key':'',
            'auth_protocal':'',
            'priv_key':'',
            'priv_protocal':'',
        }
        if sts:
            data.update({
                'snmp_engine_id':sts.snmp_engine_id,
                'snmp_version':sts.snmp_version,
                'snmptrap_host':sts.snmptrap_host,
                'snmptrap_port':sts.snmptrap_port,
                'notify_type':sts.notify_type,
                'safe_level':sts.safe_level,
                'user_name':sts.user_name,
                'auth_key':sts.auth_key,
                'auth_protocal':sts.auth_protocal,
                'priv_key':sts.priv_key,
                'priv_protocal':sts.priv_protocal,
            })

        res = {'status':'ok', 'data':data}
        return jsonify(res)

    def _save(self):
        req_data = request.get_json()
        snmp_engine_id = req_data.get('snmp_engine_id')
        snmp_version = req_data.get('snmp_version')
        snmptrap_host = req_data.get('snmptrap_host')
        snmptrap_port = req_data.get('snmptrap_port')
        notify_type = req_data.get('notify_type')
        safe_level = req_data.get('safe_level')
        user_name = req_data.get('user_name')
        auth_key = req_data.get('auth_key')
        auth_protocal = req_data.get('auth_protocal')
        priv_key = req_data.get('priv_key')
        priv_protocal = req_data.get('priv_protocal')

        if not snmp_version:
            res = {'status':'failed', 'msg':u'没有选择SNMP协议版本'}
            return jsonify(res)

        if not snmptrap_host:
            res = {'status':'failed', 'msg':u'没有填写SNMPTRAP HOST地址'}
            return jsonify(res)

        if not snmptrap_port:
            res = {'status':'failed', 'msg':u'没有填写SNMPTRAP PORT'}
            return jsonify(res)

        if not notify_type:
            res = {'status':'failed', 'msg':u'没有选择SNMPTRAP Notify Type'}
            return jsonify(res)

        if snmp_version == 'SNMPv3':
            if not safe_level:
                res = {'status':'failed', 'msg':u'没有选择安全级别'}
                return jsonify(res)
            elif safe_level == 'noAuthNoPriv':
                if not user_name:
                    res = {'status':'failed', 'msg':u'没有填写Auth Name'}
                    return jsonify(res)
            elif safe_level == 'authNoPriv':
                if not (user_name and auth_protocal and auth_key):
                    res = {'status':'failed', 'msg':u'在authNoPriv安全级别下,必须填写authname, authKey, authProtocol'}
                    return jsonify(res)
            elif safe_level == 'authPriv':
                if not (user_name and auth_protocal and auth_key and priv_protocal and priv_key):
                    res = {'status':'failed', 'msg':u'在authPriv安全级别下,必须填写authname, authKey, authProtocol, privProtocol, privKey'}
                    return jsonify(res)

            if notify_type == 'trap':
                if not snmp_engine_id:
                    res = {'status':'failed', 'msg':u'没有填写SNMP EngineId'}
                    return jsonify(res)

        sts = SnmptrapSetting.query.first()
        if not sts:
            sts = SnmptrapSetting(snmp_engine_id=snmp_engine_id,
                           snmp_version=snmp_version,
                           snmptrap_host=snmptrap_host,
                           snmptrap_port=snmptrap_port,
                           notify_type=notify_type,
                           safe_level=safe_level,
                           user_name=user_name,
                           auth_key=auth_key,
                           auth_protocal=auth_protocal,
                           priv_key=priv_key,
                           priv_protocal=priv_protocal)

            db.session.add(sts)
        else:
            SnmptrapSetting.query.update({
                                'snmp_engine_id':snmp_engine_id,
                                'snmp_version':snmp_version,
                                'snmptrap_host':snmptrap_host,
                                'snmptrap_port':snmptrap_port,
                                'notify_type':notify_type,
                                'safe_level':safe_level,
                                'user_name':user_name,
                                'auth_key':auth_key,
                                'auth_protocal':auth_protocal,
                                'priv_key':priv_key,
                                'priv_protocal':priv_protocal,
                                })
        db.session.commit()

        res = {'status':'ok', 'msg':u'SNMPTRAP 配置成功'}
        return jsonify(res)


class TencentSMSView(GeneralView):
    '''
    class desc: Tecent SMS configuration
    '''
    def get(self, action):
        action_func = {
            'list':self._list
        }
        return action_func[action]()

    def post(self, action):
        action_func = {
            'save':self._save,
        }
        return action_func[action]()

    def _list(self):
        q = TencentSMS.query.first()
        data = {'app_id':q.app_id,
                'app_key':q.app_key,
                'templ_id':q.templ_id} if q else {}

        res = {'status':'ok', 'data':data}
        return jsonify(res)

    def _save(self):
        req_data = request.get_json()
        app_id = req_data.get('app_id')
        app_key = req_data.get('app_key')
        templ_id = req_data.get('templ_id')

        ts = TencentSMS.query.first()
        if ts:
            TencentSMS.query.update({'app_id':app_id, 'app_key':app_key, 'templ_id':templ_id})
        else:
            db.session.add(TencentSMS(app_id=app_id, app_key=app_key, templ_id=templ_id))
        db.session.commit()

        res = {'status':'ok', 'msg':u'腾讯云SMS配置成功'}
        return jsonify(res)

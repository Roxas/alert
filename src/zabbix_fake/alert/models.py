# coding=utf-8
'''
define model
'''
from project import db


class EmailSMTP(db.Model):
    '''
    class desc: Email SMTP setting
    '''
    __tablename__ = 'T_EMAIL_SMTP'
    id = db.Column(db.Integer, primary_key=True)
    mail_host = db.Column(db.String(64))
    mail_port = db.Column(db.Integer)
    account = db.Column(db.String(64))
    password = db.Column(db.String(100))
    mail_subject = db.Column(db.String(64))
    mail_encoding = db.Column(db.String(8))
    mail_from = db.Column(db.String(64))

    def __repr__(self):
        return '<T_EMAIL_SMTP {}> '.format(self.id)


class SnmptrapSetting(db.Model):
    '''
    class desc: SNMP setting
    '''
    __tablename__ = 'T_SNMPTRAP_SETTING'
    id = db.Column(db.Integer, primary_key=True)
    snmp_engine_id = db.Column(db.String(32))
    snmp_version = db.Column(db.String(8))
    snmptrap_host = db.Column(db.String(64))
    snmptrap_port = db.Column(db.Integer)
    notify_type = db.Column(db.String(8)) #trap or inform
    safe_level = db.Column(db.String(16))
    user_name = db.Column(db.String(32))
    auth_key = db.Column(db.String(16))
    auth_protocal = db.Column(db.String(8))
    priv_key = db.Column(db.String(16))
    priv_protocal = db.Column(db.String(8))

    def __repr__(self):
        return '<T_SNMPTRAP_SETTING {}>'.format(self.id)


class TencentSMS(db.Model):
    '''
    class desc: Tencent SMS setting
    '''
    __tablename__ = 'T_TENCENT_SMS'
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer)
    app_key = db.Column(db.String(64))
    templ_id = db.Column(db.Integer)

    def __repr__(self):
        return '<T_TENCENT_SMS {}>'.format(self.id)


class Receiver(db.Model):
    '''
    class desc: Receiver info
    '''
    __tablename__ = 'T_RECEIVER'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32))
    user_phone = db.Column(db.String(16))
    user_email_address = db.Column(db.String(64))
    is_send_sms = db.Column(db.Boolean, default=False)
    is_send_email = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<T_RECEIVER {}>'.format(self.id)


class EmailAlertLog(db.Model):
    '''
    class desc: the log of sending email
    '''
    __tablename__ = 'T_EMAIL_ALERT_LOG'
    id = db.Column(db.Integer, primary_key=True)
    mail_to = db.Column(db.String(1024))
    content = db.Column(db.String(1024))
    error_msg = db.Column(db.String(1024))
    is_send_ok = db.Column(db.Boolean)
    try_times = db.Column(db.Integer, default=3)
    created_datetime = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<T_EMAIL_ALERT_LOG {}>'.format(self.id)




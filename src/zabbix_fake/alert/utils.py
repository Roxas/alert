# coding=utf-8
'''
file desc: some public method which are belong to alert blueprint
'''
from project import db
import traceback
import datetime
import logging
import subprocess
import json
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
'''
following is pysnmp module
'''
from pysnmp.entity import engine
from pysnmp.entity.rfc3413.context import SnmpContext
from pysnmp.smi import builder
from pysnmp.hlapi import *
'''
following is tencent sms sdk
'''
import Qcloud.Sms.sms as SmsSender
from .models import *


def send_email(to_mail, content):
    '''
    func desc: send email func,
    param to_mail: the mail address list
    param content: the content of email
    '''
    es = EmailSMTP.query.first()
    if not es:
        return False, 'Pleaes configure the tencent sms setting'
    is_success = False
    error_msg = ''
    try:
        smtp = SMTP_SSL(host=es.mail_host, port=es.mail_port, timeout=10)
        smtp.ehlo(es.mail_host)
        smtp.login(es.account, es.password)
        msg = MIMEText(content, 'plain', es.mail_encoding)
        msg['Subject'] = Header(es.mail_subject, es.mail_encoding)
        msg['from'] = es.mail_from
        msg['to'] = ','.join(to_mail)
        smtp.sendmail(es.mail_from, to_mail, msg.as_string())
        smtp.quit()
        is_success = True
    except Exception as e:
        traceback.print_exc()
        error_msg = e.message
    return is_success, error_msg


def send_notice_log(mail_to, content, send_result, error_msg):
    '''
    func desc: send email log
    param to_mail: the mail address list
    param content: the content of email
    param send_result: the result of sending email
    param error_msg: the error when sending email
    '''
    if mail_to:
        ea_log = EmailAlertLog(mail_subject=subject,
                            mail_to=mail_to,
                            content=content,
                            error_msg=error_msg,
                            is_send_ok=send_result,
                            try_times=1,
                            created_datetime=datetime.datetime.now())

        db.session.add(ea_log)
        db.session.commit()


def send_tencent_sms(phone_list, content):
    '''
    func desc: use tencent SDK send sms message
    param phone_list: the phone list of users
    param content: the content of send tencent sms
    '''
    tencent_sms_conf = TencentSMS.query.first()
    if not tencent_sms_conf:
        return False, 'Pleaes configure the tencent sms setting'

    multi_sender = SmsSender.SmsMultiSender(tencent_sms_conf.app_id, tencent_sms_conf.app_key)
    result = multi_sender.send_with_param("86",
                                          phone_list,
                                          tencent_sms_conf.templ_id,
                                          [content],
                                           "", "", "")
    # result = multi_sender.send(0, "86", phone_list, content, "", "")
    rsp = json.loads(result)
    return True, rsp


def send_snmp_trap(content):
    '''
    func desc: send content to SNMP trap server, the func is still unstable
    '''
    auth_protocals = {
        'MD5': usmHMACMD5AuthProtocol,
        'SHA': usmHMACSHAAuthProtocol,
    }

    priv_protocals = {
        'DES': usmDESPrivProtocol,
    }

    sts = SnmptrapSetting.query.first()
    if not sts:
        return False, 'Please configure the SNMPTrap setting'

    snmp_engine_id = sts.snmp_engine_id
    snmp_version = sts.snmp_version
    safe_level = sts.safe_level
    user_name = sts.user_name
    auth_key = sts.auth_key
    auth_protocal = auth_protocals.get(sts.auth_protocal)
    priv_key = sts.priv_key
    priv_protocal = priv_protocals.get(sts.priv_protocal)
    snmptrap_host = sts.snmptrap_host
    snmptrap_port = sts.snmptrap_port
    notify_type = sts.notify_type

    if snmp_engine_id:
        snmp_engine = engine.SnmpEngine(snmpEngineID=snmp_engine_id)
    else:
        snmp_engine = engine.SnmpEngine()

    params = {}
    if snmp_version == 'SNMPv3':
        if safe_level == 'noAuthNoPriv':
            params.update({'userName':user_name})
        elif safe_level == 'authNoPriv':
            params.update({'userName':user_name,
                        'authProtocol':auth_protocal,
                        'authKey':auth_key})
        elif safe_level == 'authPriv':
            params.update({'userName':user_name,
                        'authProtocol':auth_protocal,
                        'authKey':auth_key,
                        'privProtocol':priv_protocal,
                        'privKey':priv_key})
        uud = UsmUserData(**params)
    else:
        uud = CommunityData('public', mpModel=1)

    g = sendNotification(snmp_engine,
                            uud,
                            UdpTransportTarget((snmptrap_host, snmptrap_port)),
                            ContextData(),
                            notify_type,
                            NotificationType(
                            ObjectIdentity('1.3.6.1.4.1.50490')
                            ).addVarBinds(
                            ('1.3.6.1.4.1.50490.1.1.1.1.1', OctetString(content)),
                        )
                    )
    return True, 'OK'


def send_notice(email_message, sms_message, snmp_message):
    '''
    func desc: send notice according the different messages include(email, sms, snmp)
    param email_message: send email message if not empty string
    param sms_message: send sms messsage if not empty string
    param snmp_message: send snmp message if not empty string
    '''
    if email_message:
        recevier_qs = Receiver.query.filter_by(is_send_mail=True).all()
        mail_address_list = [q.user_email_address for q in recevier_qs]

        if mail_address_list:
            mail_address_list = list(set(mail_address_list))
            szemails = ','.join(mail_address_list)
            result, error_msg = send_email(email_message, mail_address_list)
            send_notice_log(szemails, email_message, result, error_msg)

    if sms_message:
        receiver_qs = Receiver.query.filter_by(is_send_sms=True).all()
        phone_list = [q.user_phone for q in receiver_qs]
        send_tencent_sms(tencent_sms_conf.app_id,
                         tencent_sms_conf.app_key,
                         tencent_sms_conf.templ_id,
                         phone_list,
                         sms_message)

    if snmp_message:
        send_snmp_trap(snmp_message)
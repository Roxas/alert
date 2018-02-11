'''
the url route file
'''
from alert.views import EmailSMTPView, ReceiverView, EmailAlertLogView, SnmptrapSettingView,\
                        TencentSMSView
from . import alert


alert.add_url_rule('/email/smtp/conf/<action>', view_func=EmailSMTPView.as_view('email_smtp_mgr'))

alert.add_url_rule('/receiver/<action>', view_func=ReceiverView.as_view('receiver_mgr'))

alert.add_url_rule('/email/logs.json', view_func=EmailAlertLogView.as_view('email_logs'))

alert.add_url_rule('/snmptrap/conf/<action>', view_func=SnmptrapSettingView.as_view('snmptrap_conf_mgr'))

alert.add_url_rule('/tencent/sms/conf/<action>', view_func=TencentSMSView.as_view('tencent_sms_mgr'))

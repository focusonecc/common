# -*- encoding: utf-8 -*-
from django.conf import  settings
import requests
def send_sms(phone, content):
    """
    Used yunpian to send message
    """
    if settings.SMS_DEBUG:
        print('Sms will be send as: %s, %s', phone, content)
        return True, ''
    apikey = settings.YUNPIAN['apikey']
    url = 'http://yunpian.com/v1/sms/send.json'
    data = {
        'apikey': apikey,
        'mobile': phone,
        'text': content
    }

    try:
        response = requests.post(url, data).json()
        if response['code'] == 0:
            return True, ''
        return False, response['msg']
    except Exception as e:
        return False, e.message

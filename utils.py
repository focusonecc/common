# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-09-08 10:55:37
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-08 16:04:22

import re
import random
import string
import uuid
import time
import six
import requests
from datetime import datetime
from django.utils import timezone
from django.conf import settings


def gen_random_str(length, rtype='any'):
    """
    rtype: specify which type of character will in the final string
    rtype can be: [any|char|digit]
    """
    if rtype == 'digit':
        return ''.join(random.sample(string.digits, length))

    if rtype == 'char':
        return ''.join(random.sample(string.ascii_letters, length))

    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def gen_random_digit_code(length=6):
    """
    >>> code=gen_random_digit_code()
    >>> code.isdigit()
    True
    """
    return gen_random_str(length, 'digit')


def gen_random_char_code(length=10):
    return gen_random_str(length, 'char')


def gen_uuid():
    """
    Generate a UUID value
    """
    return uuid.uuid4().hex


def validate_uuid(uuid_str, version=4):
    uuid_str = uuid_str or ''

    if isinstance(uuid_str, (uuid.UUID)):
        return uuid_str

    try:
        value = uuid.UUID(uuid_str, version=version)
    except ValueError:
        return None
    else:
        return value


def datetime2timestamp(value):
    """
    Convert a datetime instance to a timstamp value
    """
    if hasattr(value, 'tzinfo') and value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
        value = timezone.localtime(value)

    return int(time.mktime(value.timetuple()))


def timestamp2datetime(value):
    """
    Convert a timestamp value to a timezone aware datetime object
    """
    return timezone.make_aware(datetime.fromtimestamp(value))


def get_absolute_url_path(url):
    """
    Used to build an absolute url path for the given url string
    """
    if not isinstance(url, six.string_types):
        raise ValueError('url should be a string type value')

    if not url:
        return url

    if url.startswith('http://') or url.startswith('https://'):
        return url

    return '{}{}'.format(settings.HOST, url)


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


def validate_phone(phone):
    m = re.match('^\d{11}', phone)
    if m is not None:
        return True
    return False


def validate_required_params(json_data, requires=None):
    """
    Validate if the field of all requires in the json_data
    """
    requires = requires or []
    for field in requires:
        if field not in json_data:
            return False
    return True


def get_client_ip(request):
    """
    Used to fetch request client's ip address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR') or ''

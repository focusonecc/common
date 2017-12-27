# -*- encoding: utf-8 -*-
import six
import warnings
from django.conf import settings



def get_absolute_url_path(url):
    """
    用来为系统中给定的url路径构造其绝对路径
    """
    if not isinstance(url, six.string_types):
        raise ValueError('url should be a string type value')

    if not url:
        warnings.warn('The given url should not be empty!')
        return url

    if url.startswith('http://') or url.startswith('https://'):
        return url

    return '{}{}'.format(settings.HOST, url)

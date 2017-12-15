# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-09-08 10:21:11
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-11 21:34:59

from .settings import RESPONSE_CODE_NAME, RESPONSE_MSG_NAME


class MessageCode(object):
    """
    The common api response status code & message which returned to the app client
    """

    def __init__(self, code, message):
        init_data = {
            RESPONSE_CODE_NAME: code,
            RESPONSE_MSG_NAME: message
        }
        self.__dict__.update(init_data)

    @property
    def code(self):
        return self.__dict__.get(RESPONSE_CODE_NAME)

    @property
    def message(self):
        return self.__dict__.get(RESPONSE_MSG_NAME)

    def __str__(self):
        return '{}:{}'.format(self.code, self.message)

    def __unicode__(self):
        return self.__str__()


# Base message & code
Unknown = MessageCode(-1, u'Unknow reason!')
OK = MessageCode(1, '')


# Parameter related message & code
PARAM_REQUIRED = MessageCode(1000, u'Parameter is requried!')
PARAM_INVALID = MessageCode(1001, u'Invalid Parameter!')
UUID_INVALID = MessageCode(1002, u'Invalid UUID!')
CODE_INVALID = MessageCode(1003, u'Invalid Code!')
EXPIRED = MessageCode(1004, u'Expired!')


# HTTP request related message & code
FREQUENT_REQUEST = MessageCode(1100, u'Request too frequent!')


# Authentication related message & code
AUTH_NEEDED = MessageCode(1200, u'Unauthorized!')

# DB model related message & code
DB_ERROR = MessageCode(1300, u'Database error!')
DB_OBJ_NOT_FOUND = MessageCode(1301, u'Object not found!')
DB_OBJ_DUPLICATED = MessageCode(1302, u'Duplicated Object!')

# 3rd party Service related message & code
YUNPIAN_SERVICE_ERROR = MessageCode(1400, u'YUNPIAN API Service error!')

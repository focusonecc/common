# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-09-08 10:22:29
# @Last Modified by:   theo-l
# @Last Modified time: 2017-09-08 11:01:26

# API response status code & message pair
import os
RESPONSE_CODE_NAME = 'code'
RESPONSE_MSG_NAME = 'msg'

# 通用的log文件所在目录
COMMON_LOG_BASE_DIR='/usr/log'

# common model fields, which used in the base resource class
MODEL_COMMON_FIELDS = ['created_at', 'enabled', 'updated_at']

LOGGING = {
    'version'                 : 1,
    'disable_existing_loggers': False,
    'formatters'              : {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s'
        },
        'simple' : {
            'format': '[%(module)s.%(funcName)s] %(message)s'
        },
    },
    'handlers'                : {
        'debug'   : {
            'level'    :  'DEBUG',
            'class'    : 'logging.FileHandler',
            'filename' : os.path.join(COMMON_LOG_BASE_DIR, 'django-debug.log'),
            'formatter': 'verbose'
        },
        'warning' : {
            'level'    :  'WARNING',
            'class'    : 'logging.FileHandler',
            'filename' : os.path.join(COMMON_LOG_BASE_DIR, 'django-warning.log'),
            'formatter': 'verbose'
        },

        'console': {
            'level'    : 'DEBUG' ,
            'class'    : 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers'                 : {

        'debug': {
            'handlers' : ['debug', 'console'],
            'level'    : 'DEBUG',
            'propagate': True,
        },

        'warning': {
            'handlers' : ['warning', 'console'],
            'level'    : 'WARNING',
            'propagate': True,
        },
        'system': {
            'handlers' : ['warning', 'console'],
            'level'    :  'WARNING',
            'propagate': True,
        },
        'api'   : {
            'handlers' : ['debug', 'console'],
            'level'    : 'DEBUG' ,
            'propagate': True,
        },
    },
}



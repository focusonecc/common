# -*- encoding: utf-8 -*-
"""
比较常见的一些工具函数集合
"""

import random
import string
import uuid

# 生成随机字符串的内容的字符类型
RANDOM_ANY = 'any'
RANDOM_DIGIT = 'digit'
RANDOM_LETTER= 'letter'
RANDOM_UPPER='upper'
RANDOM_LOWER='lower'

def get_random_str(length, rtype=RANDOM_ANY):
    """
    根据传入的rtype 参数来生成不同类型的随机字符串
    """
    if rtype == RANDOM_DIGIT:
        return ''.join(random.sample(string.digits, length))
    if rtype== RANDOM_LETTER:
        return ''.join(random.sample(string.ascii_letters,length))
    if rtype == RANDOM_LOWER:
        return  ''.join(random.sample(string.ascii_lowercase, length))
    if rtype == RANDOM_UPPER:
        return ''.join(random.sample(string.ascii_uppercase, length))

    return ''.join(random.sample(string.ascii_letters+string.digits, length))


def gen_random_digit_code(length=6):
    # 生成随机数字字符串
    return get_random_str(length, rtype=RANDOM_DIGIT)

def gen_random_letter_code(length=6):
    # 生成随机字母字符串
    return get_random_str(length, rtype=RANDOM_LETTER)

def gen_random_uppercase_code(length=6):
    # 生成随机大写字母字符串
    return get_random_str(length, rtype=RANDOM_UPPER)

def gen_random_lowercase_code(length=6):
    # 生成随机小写字母字符串
    return get_random_str(length, rtype=RANDOM_LOWER)


def gen_uuid():
    """
    生成一个UUID值
    """
    return uuid.uuid4().hex


def validate_uuid(uuid_str, version=4):
    """
    验证一个uuid字符串值得合法性
    """
    uuid_str = uuid_str or ''

    if isinstance(uuid_str, (uuid.UUID)):
        return uuid_str

    try:
        value = uuid.UUID(uuid_str, version=version)
    except ValueError:
        return None
    else:
        return value

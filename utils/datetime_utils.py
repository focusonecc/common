# -*- encoding: utf-8 -*-
from datetime import datetime
import time
from django.utils import timezone


def datetime2timestamp(value):
    """
    Convert a datetime instance to a timstamp value
    将日期时间实例转换为一个时间戳值
    """
    if hasattr(value, 'tzinfo') and value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
        value = timezone.localtime(value)

    return int(time.mktime(value.timetuple()))


def timestamp2datetime(value):
    """
    将一个时间戳值转换为系统所在时区的日期时间实例
    """
    return timezone.make_aware(datetime.fromtimestamp(value))


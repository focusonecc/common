from datetime import datetime
import time
from django.utils import timezone


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


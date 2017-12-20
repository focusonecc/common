import random
import string
import uuid


def gen_random_digit_code(length=6):
    return ''.join(random.sample(string.digits, length))


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

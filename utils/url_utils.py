import six
from django.conf import settings


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

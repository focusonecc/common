# -*- encoding: utf-8 -*-


class ErrorCode(object):

    def __init__(self, status_code, detail):
        self._code = status_code
        self._detail = detail

    @property
    def code(self):
        return self._code

    @property
    def detail(self):
        return self._detail

    def __str__(self):
        return self._code

    def __unicode__(self):
        return self.__str__()


# common
UNKNOWN_ERROR = ErrorCode(-1, u'Unknown error!')
SUCCESS = ErrorCode(0, u'Success!')
REQUIRED = ErrorCode(1000, u"parameter required error!")
DUPLICATED = ErrorCode(1001, u"unique entry error!")
NOT_ALLOWED = ErrorCode(1002, u"action not allowed error!")
AUTH_NEEDED = ErrorCode(1003, u"unauthorized error!")
BAD_PARAMS = ErrorCode(1004, u" parameter error!")
NOT_EXISTS = ErrorCode(1005, u"object not exist error!")
EXPIRED = ErrorCode(1006, u'Data expired error!')

# auth error
# TODO


if __name__ == '__main__':
    for code in (UNKNOWN_ERROR, SUCCESS):
        print code.code, code.detail

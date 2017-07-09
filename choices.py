# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-07-08 21:16:46
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-08 21:57:41


import six


class ChoiceItem(object):

    def __init__(self, value, desc):
        self._value = value
        self._desc = desc

    @property
    def value(self):
        return self._value

    @property
    def desc(self):
        return self._desc

    def getvalue(self):
        return (self.value, self.desc)

    def __str__(self):
        return str(self.getvalue())


class BaseChoice(type):
    """
    The base class for all Choices
    provide a 'choices' attribute to access for all Choice class
    """

    def __new__(metaclass, cls, bases, attr):
        base_meta = super(BaseChoice, metaclass).__new__(metaclass, cls, bases, attr)
        if attr:
            choices = []
            for field, value in attr.items():
                if isinstance(value, ChoiceItem):
                    choices.append(value.getvalue())
                    setattr(base_meta, field, value.value)
            if choices:
                choices = tuple(choices)
                setattr(base_meta, 'choices', choices)
        return base_meta


class HttpMethodChoice(six.with_metaclass(BaseChoice)):
    GET = ChoiceItem(1, 'HTTP GET request method')
    POST = ChoiceItem(2, 'HTTP POST reqeust method')
    PUT = ChoiceItem(3, 'HTTP PUT request method')
    PATCH = ChoiceItem(4, 'HTTP PATCH request method')
    DELETE = ChoiceItem(5, 'HTTP DELETE request method')

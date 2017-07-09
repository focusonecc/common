# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-07-08 21:16:46
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-08 23:49:33


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


class ChoiceMeta(type):
    """
    Meta class for all choice class
    """

    def __new__(metaclass, cls, bases, attr):
        """
        1. parse each ChoiceItem instance attribute into a special attribute 'choices'
        2. reset the ChoiceItem attribute value to the 'value' of ChoiceItem item
        """
        base_meta = super(ChoiceMeta, metaclass).__new__(metaclass, cls, bases, attr)
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


class BaseChoice(six.with_metaclass(ChoiceMeta)):
    """
    Base class of all choices

    Usage:

        # customize a subclass of choice
        class ColorChoice(BaseChoice):
            RED = ChoiceItem(1, 'Red')
            GREEN = ChoiceItem(2, 'Green')

        # in model definition
        class DemoModel(models.Model):
            color = models.IntegerField(choices=ColorChoice.choices, default=ColorChoice.RED)
    """
    pass


class HttpMethodChoice(BaseChoice):
    """
    General API request method choices
    """
    GET = ChoiceItem(1, 'HTTP GET')
    POST = ChoiceItem(2, 'HTTP POST')
    PUT = ChoiceItem(3, 'HTTP PUT')
    PATCH = ChoiceItem(4, 'HTTP PATCH')
    DELETE = ChoiceItem(5, 'HTTP DELETE')

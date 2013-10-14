from abc import ABCMeta
from .validators import IntegerValidator, StringValidator


class Field(object):
    """
    The base field class. A Field is part of a Model class. It define
    an aspect of a ressource.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, **options):
        self.name = name
        self.options = options


class IntegerField(Field):
    base_type = int
    validators = [IntegerValidator()]


class StringField(Field):
    base_type = basestring
    validators = [StringValidator()]


class PkField(Field):
    base_type = int
    validators = []


class StringPkField(PkField):
    base_type = str
    validator = []

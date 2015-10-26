"""
Fields type used with models
"""

from abc import ABCMeta
from .validators import (IntegerValidator, StringValidator,
                         FloatValidator, SQLiteForeign)


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
    """
    An integer field. python type int, with IntegerValidator
    """
    base_type = "integer"
    validators = [IntegerValidator()]
    example = 42


class StringField(Field):
    """
    An string field. python type basestring (either str or
    basestring), with StringValidator
    """
    base_type = "string"
    validators = [StringValidator()]
    example = "Hello World"


class PkField(Field):
    """
    PkField is a mandatory field for a model. It define the unique
    ressource identifier. If your unique field is not an integer
    field, you have to inherit from this class and implement your own.
    see StringPkField
    """
    base_type = "integer"
    validators = []
    example = 42


class ForeignKeyField(object):

    def __init__(self, name, **options):
        self.validators = [SQLiteForeign(**options), IntegerValidator()]
        super(ForeignKeyField, self).__init__(name, **options)


class IntForeign(ForeignKeyField, Field):
    """
    A type of integer and a Foreign key to check
    """
    base_type = "integer"
    example = 42


class StringForeingKey(ForeignKeyField, Field):
    """
    A type of string and a Foreign key to check
    """
    base_type = "string"
    example = "hackme"

    def __init__(self, name, **options):
        super(StringForeingKey, self).__init__(name, **options)
        self.validators = [SQLiteForeign(**options), StringValidator()]


class StringPkField(PkField):
    """
    A string based PkField
    """
    base_type = "string"
    validators = [StringValidator()]
    example = "i6HOCjvZMQ4"


class TimestampField(Field):
    """
    A unix timestamp
    """
    base_type = "float"
    validators = [FloatValidator()]
    example = 34.8

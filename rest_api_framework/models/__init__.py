"""
Model are the representation of your ressources.
"""
from validators import IntegerValidator, StringValidator


class Model(object):
    """
    The base model class.
    A model object represent a ressource to be plugged in a datastore
    """
    def get_fields_name(self):
        return [field.name for field in self.fields]

    def get_fields(self):
        return [field for field in self.fields]

    def get_field(self, field_name):
        for field in self.fields:
            if field.name == field_name:
                return field


class Field(object):
    """
    The base field class. A Field is part of a Model class. It define
    an aspect of a ressource.
    """
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

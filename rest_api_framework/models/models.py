"""
Define models describing a ressource
"""
from abc import ABCMeta
from . import fields


class Model(object):
    """
    The base model class.
    A model object represent a ressource to be plugged in a datastore
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.pk_field = [
            field for field in self.fields if isinstance(
                field, fields.PkField)][0]

    def get_fields_name(self):
        """
        return the name of each fields registered with this model
        """
        return [field.name for field in self.fields]

    def get_fields(self):
        """
        return each fields registered with this model
        """
        return [field for field in self.fields]

    def get_field(self, field_name):
        """
        return a single field matching the name of the provided field_name.
        None if no match can be found
        """
        for field in self.fields:
            if field.name == field_name:
                return field
        return None

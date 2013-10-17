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

    fields = None

    def __init__(self):
        pk_field = [
            field for field in self.fields if isinstance(
                field, fields.PkField)]
        if len(pk_field) != 1:
            raise ValueError
        self.pk_field = pk_field[0]

    def get_schema(self):
        fields = self.get_fields()
        response = {}
        for field in fields:
            if field == self.pk_field:
                continue
            response[field.name] = {"type": str(field.base_type),
                                    "example": field.example
                                    }
            if field.options.get("required") and\
                    field.options["required"] is True:
                response[field.name]['required'] = "true"
        return response

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

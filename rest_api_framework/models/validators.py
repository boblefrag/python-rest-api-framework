"""
Validators to check the values of Fields instances
"""
from abc import ABCMeta, abstractmethod


class Validator(object):
    """
    Base Validator class
    Used to validate data format
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, field):
        """
        Method to validate that a field is formated as expected or is
        of correct type/class
        """
        raise NotImplementedError


class IntegerValidator(Validator):
    """
    Validate that a value is of type int
    """

    def validate(self, field):
        if isinstance(field, int):
            return True
        return False


class StringValidator(Validator):
    """
    Validate that a value is of type basestring (either str or unicode)
    """

    def validate(self, field):
        if isinstance(field, basestring):
            return True
        return False

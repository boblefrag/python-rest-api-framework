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
    def validate(self, field, *args):
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
        """
        Check if field is an instance of type 'int'
        """
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


class FloatValidator(Validator):
    """
    Validate that a value is of float type
    """

    def validate(self, field):
        if isinstance(field, float):
            return True
        return False


class SQLiteForeign(Validator):
    """
    Validate that the foreign row exists
    """
    need_datastore = True

    def __init__(self, **options):
        self.options = options

    def validate(self, field, datastore):

        cursor = datastore.conn.cursor()

        cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
        # cursor = datastore.conn.cursor()
        query = "SELECT {0} FROM {1} WHERE {2}=?".format(
            self.options["foreign"]["column"],
            self.options["foreign"]["table"],
            self.options["foreign"]["column"],
        )
        cursor.execute(query, (field, ))
        if cursor.fetchone():
            return True
        return False

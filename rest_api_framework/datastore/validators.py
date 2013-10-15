"""
Base implementation of datastore validators. Those validators acts on
the data they received but need a datastore to validate data
"""
from werkzeug.exceptions import BadRequest


class Validator(object):

    def __init__(self, *fields):
        self.fields = fields
        self.datastore = None

    def validate(self, datastore, data):
        raise NotImplementedError


class UniqueTogether(Validator):

    def validate(self, datastore, data):
        """
        Check if a record with the same fields already exists in the
        database.
        """
        self.datastore = datastore
        query_dict = {}
        for k, v in data.iteritems():
            if k in self.fields:
                query_dict[k] = v
        resp = datastore.get_list(**query_dict)
        if len(resp) > 0:
            raise BadRequest("{0} must be unique together".format(
                    ",".join(self.fields)))

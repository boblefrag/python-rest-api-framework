"""
Enable partials response from the api. With partials response, only a
subset of fields are send back to the request user.

DataStore are responsible for implementing partial options
"""


class Partial(object):
    """
    The base implementation of partial response.
    """
    def __init__(self, partial_keyword="fields"):
        self.partial_keyword = partial_keyword

    def get_partials(self, **kwargs):
        """
        This partial implementation wait for a list of fields
        separated by comma.  Other implementations are possible. Just
        inherit from this base class and implement your own
        get_partials method.

        get_partials does not check that the fields are part of the
        model. Datastore get_list will check for it and raise an error
        if needed.
        """
        partial_fields = []
        if kwargs.get(self.partial_keyword):
            partial_fields = kwargs.pop(self.partial_keyword).split(',')
        return partial_fields, kwargs

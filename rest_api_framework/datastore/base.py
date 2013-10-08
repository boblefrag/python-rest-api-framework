from werkzeug.exceptions import BadRequest


class DataStore(object):
    """
    define a source of data. Can be anything fron database to other
    api, files and so one
    """

    def __init__(self, data, **options):
        """
        Set the ressource datastore
        """
        self.data = data
        self.options = options
        self.description = options["description"]

    def paginate(self, data, **kwargs):
        """
        Naive implementation of pagination. Ressource_list must implement
        indexing in a clever way. This naive implementation does not check
        for negative index nor outbound index.
        HINT for python generator:

        import itertools
        class Indexable(object):
        def __init__(self,it):
            self.it=it
        def __iter__(self):
            for elt in self.it:
                yield elt
        def __getitem__(self,index):
            try:
                return next(itertools.islice(self.it,index,index+1))
            except TypeError:
                return list(itertools.islice(self.it,
                                             index.start,
                                             index.stop,
                                             index.step
                                             )
                            )
        """
        start = 0
        end = self.options.get('paginate_by', None)
        if "start" in kwargs:
            start = int(kwargs['start'])
            end = start + self.options['paginate_by']
        elif "end" in kwargs:
            end = int(kwargs['end'])
            start = end - int(kwargs['end'])

        return data[start:end]

    def validate(self, data):
        """
        Check if data send are valide for objec creation
        """

        if not isinstance(data, dict):
            raise BadRequest()
        for k, v in self.description.iteritems():
            if self.description[k]['required']:
                if not k in data or \
                        not isinstance(data[k],
                                       self.description[k]['type']
                                       ):
                    raise BadRequest()

    def validate_fields(self, data):
        """
        Validate some fields of the ressource
        """
        if not isinstance(data, dict):
            raise BadRequest()
        for k, v in data.iteritems():
            if k not in self.description.iterkeys():
                raise BadRequest()
            elif not isinstance(v, self.description[k]["type"]):
                raise BadRequest()

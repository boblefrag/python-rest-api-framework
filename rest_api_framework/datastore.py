from werkzeug.exceptions import BadRequest, NotFound


class DataStore(object):
    """
    define a source of data. Can be anything fron database to other
    api, files and so one
    """

    def get_description(self):
        raise NotImplemented

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
        end = self.options['paginate_by']
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


class PythonListDataStore(DataStore):
    """
    a datastore made of list of dicts
    """

    def get_description(self):
        return {
            "name": {
                "type": basestring, "required": True},
            "age": {
                "type": int, "required": True},
            "id": {
                "type": "autoincrement", "required": False}
            }

    def __init__(self, data, **options):
        """
        Set the ressource datastore
        """
        self.data = data
        self.options = options
        self.description = self.get_description()

    def get(self, identifier):
        """
        return an object matching the uri or None
        """
        print "called", identifier
        for elem in self.data:
            if elem['id'] == identifier:
                return elem
        raise NotFound

    def filter(self, **kwargs):
        data = self.data
        for k, v in kwargs.iteritems():
            try:
                data = [elem for elem in data if elem[k] == v]
            except KeyError:
                raise BadRequest()
        return data

    def get_list(self, **kwargs):
        """
        return all the objects paginated if needed
        """
        start = kwargs.pop("start", None)
        data = self.filter(**kwargs)
        return self.paginate(data, start=start)

    def create(self, data):

        self.validate(data)
        obj = {}
        for k, v in data.iteritems():
            if k in self.description.iterkeys():
                obj[k] = v

        for field in self.description.iterkeys():
            if self.description[field]["type"] == "autoincrement":
                self.data.sort(lambda a, b: a[field] > b[field])
                last = self.data[-1][field]
                obj[field] = last + 1

        self.data.append(obj)
        return obj["id"]

    def update(self, obj, data):
        """
        Update a single object
        """
        # chek if the object already exists
        self.get(obj['id'])
        # check the fields to be updated
        self.validate_fields(data)
        # update the object
        for k, v in data.iteritems():
            obj[k] = v

        # save it in the datastore
        self.data[obj['id']] = obj
        # return the object
        return obj

    def delete(self, identifier):
        obj = self.get(identifier)
        self.data.remove(obj)

from werkzeug.exceptions import BadRequest, NotFound
import sqlite3


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


class PythonListDataStore(DataStore):
    """
    a datastore made of list of dicts
    """

    def get(self, identifier):
        """
        return an object matching the uri or None
        """
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
                pass
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


class SQLDataStore(DataStore):

    wrapper = {int: "integer",
               float: "real",
               basestring: "text",
               "autoincrement": "integer primary key autoincrement"
               }

    def __init__(self, data, **options):
        conn = sqlite3.connect(data["name"])
        c = conn.cursor()
        table = data["table"]
        super(SQLDataStore, self).__init__({"conn": conn, "table": table},
                                           **options)
        fields = ", ".join(
            ["{0} {1}".format(k,
                              self.wrapper[v['type']]
                              ) for k, v in self.description.iteritems()])
        sql = 'create table if not exists {0} ({1})'.format(table, fields)
        c.execute(sql)
        conn.commit()

    def filter(self, **kwargs):
        kwargs['query'] += ' FROM {0}'
        return kwargs

    def paginate(self, data, **kwargs):

        limit = self.options.get('paginate_by', None)
        if kwargs.get("start", None):
            data["query"] += " WHERE id >= {0}".format(kwargs["start"])

        if kwargs.get("end", None):
            data["query"] += " WHERE id < {0} order by id DESC".format(
                kwargs["end"])
        if limit:
            data["query"] += " LIMIT {0}".format(limit)

        print data["query"]

        c = self.data['conn'].cursor()
        c.execute(data["query"].format(self.data['table']))
        objs = []
        for elem in c.fetchall():
            fields = [k for k in self.description.iterkeys()]
            objs.append(dict(zip(fields, elem)))
        if kwargs.get("end", None):
            objs.reverse()
        return objs

    def get_list(self, **kwargs):
        """
        return all the objects, paginated if needed
        """
        fields = ", ".join([k for k in self.description.iterkeys()])
        kwargs["query"] = 'SELECT {0}'.format(fields)
        start = kwargs.pop("start", None)
        end = kwargs.pop("end", None)
        data = self.filter(**kwargs)
        return self.paginate(data, start=start, end=end)

    def get(self, identifier):

        c = self.data['conn'].cursor()
        fields = ", ".join([k for k in self.description.iterkeys()])
        query = "select {0} from {1} where id=?".format(
            fields,
            self.data["table"])
        c = self.data['conn'].cursor()
        c.execute(query, (identifier,))
        obj = c.fetchone()
        if obj:
            fields = [k for k in self.description.iterkeys()]
            return dict(zip(fields, obj))
        else:
            raise NotFound

    def create(self, data):
        self.validate(data)
        fields = []
        values = []
        for k, v in data.iteritems():
            if k in self.description.iterkeys():
                fields.append(k)
                values.append(v)
        c = self.data['conn'].cursor()
        query = "insert into {0} {1} values {2}".format(
            self.data["table"],
            tuple(fields),
            tuple(values))
        c.execute(query)
        return c.lastrowid
        # qs = " and ".join(["{0}={1}".format(f, v) for f, v in zip(fields, values)])
        # query = "select id from {0} where {1}".format(self.data["table"],
        #                                               qs)
        # print query

    def update(self, obj, data):
        self.get(obj['id'])
        self.validate_fields(data)
        fields = []
        values = []
        for k, v in data.iteritems():
            if k in self.description.iterkeys():
                fields.append(k)
                values.append(v)
        c = self.data['conn'].cursor()
        update = " ".join(["{0}='{1}'".format(f, v) for f, v in zip(fields, values)])
        query = "update {0} set {1}".format(
            self.data["table"],
            update
            )
        c.execute(query)
        return self.get(obj['id'])

    def delete(self, identifier):
        obj = self.get(identifier)
        c = self.data['conn'].cursor()
        query = "delete from {0} where id={1}".format(self.data["table"],
                                                      identifier)
        c.execute(query)

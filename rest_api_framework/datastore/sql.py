from base import DataStore
from werkzeug.exceptions import NotFound
import sqlite3


class SQLiteDataStore(DataStore):

    wrapper = {int: "integer",
               float: "real",
               basestring: "text",
               "autoincrement": "integer primary key autoincrement"
               }

    def __init__(self, data, **options):
        conn = sqlite3.connect(data["name"])
        c = conn.cursor()
        table = data["table"]
        super(SQLiteDataStore, self).__init__({"conn": conn, "table": table},
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
        args = []
        limit = self.options.get('paginate_by', None)
        if kwargs.get("start", None):
            data["query"] += " WHERE id >=?"
            args.append(kwargs['start'])
        if kwargs.get("end", None):
            data["query"] += " WHERE id < ? order by id DESC"
            args.append(kwargs['end'])
        if limit:
            data["query"] += " LIMIT {0}".format(limit)

        c = self.data['conn'].cursor()
        c.execute(data["query"].format(self.data['table']), tuple(args))
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
        update = " ".join(["{0}='{1}'".format(f, v) for f, v in zip(fields,
                                                                    values)])
        query = "update {0} set {1}".format(
            self.data["table"],
            update
            )
        c.execute(query)
        return self.get(obj['id'])

    def delete(self, identifier):
        self.get(identifier)
        c = self.data['conn'].cursor()
        query = "delete from {0} where id={1}".format(self.data["table"],
                                                      identifier)
        c.execute(query)

"""
Implement some datastore based on SQL databases
"""

from .base import DataStore
from rest_api_framework.models import PkField
from werkzeug.exceptions import NotFound, BadRequest
import sqlite3


class SQLiteDataStore(DataStore):
    """
    Define a sqlite datastore for your ressource.  you have to give
    __init__ a data parameter containing the information to connect to
    the database and to the table.

    example:

    .. code-block:: python

       data={"table": "tweets",
             "name": "test.db"}
       model = ApiModel
       datastore = SQLiteDataStore(data, **options)

    SQLiteDataStore implement a naive wrapper to convert Field
    types into database type.

    * int will be saved in the database as INTEGER
    * float will be saved in the database as REAL
    * basestring will be saved in the database as TEXT
    * if the Field type is PKField, is a will be saved as
      PRIMARY KEY AUTOINCREMENT

    As soon as the datastore is instanciated, the database is create
    if it does not exists and table is created too

    .. note::

       - It is not possible to use :memory database either.
         The connection is closed after each operations
    """

    wrapper = {"integer": "integer",
               "float": "real",
               "string": "text"
               }

    def __init__(self, ressource_config, model, **options):

        self.db = ressource_config["name"]
        conn = sqlite3.connect(ressource_config["name"])
        cursor = conn.cursor()
        table = ressource_config["table"]
        super(SQLiteDataStore, self).__init__({"conn": conn, "table": table},
                                              model,
                                              **options)
        self.create_database(cursor, table)
        conn.commit()
        conn.close()
        self.fields = self.model.get_fields()

    def create_database(self, cursor, table):
        statement = []
        for field in self.model.get_fields():
            query = "{0} {1}".format(field.name, self.wrapper[field.base_type])
            if isinstance(field, PkField):
                query += " primary key autoincrement"
            statement.append(query)
            if "required" in field.options and field.options['required'] is True:
                query += " NOT NULL"
        fields = ", ".join(statement)
        for field in self.model.get_fields():

            if "foreign" in field.options:
                fields += ",FOREIGN KEY ({0}) REFERENCES {1}({2})".format(
                    field.name, field.options["foreign"]["table"],
                    field.options["foreign"]["column"]
                    )

        sql = 'create table if not exists {0} ({1})'.format(table, fields)
        cursor.execute(sql)

    def get_connector(self):
        """
        return a sqlite3 connection to communicate with the table
        define in self.db
        """
        conn = sqlite3.connect(self.db)
        conn.execute('pragma foreign_keys=on')
        return conn

    def filter(self, **kwargs):
        """
        Change kwargs["query"] with "WHERE X=Y statements".  The
        filtering will be done with the actual evaluation of the query
        in :meth:`~.SQLiteDataStore.paginate` the sql can then be lazy
        """
        kwargs['query'] += ' FROM {0}'
        return kwargs

    def count(self, **data):
        cdt = self.build_conditions(data)
        if len(cdt) == 0:
            query = "SELECT COUNT (*) FROM {0}".format(
                self.ressource_config['table'])
        else:
            cdt = " AND  ".join(cdt)
            query = "SELECT COUNT (*) FROM {0} WHERE {1}".format(
                self.ressource_config['table'],
                cdt
                )
        cursor = self.get_connector().cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]

    def build_conditions(self, data):
        return [
            ["{0}='{1}'".format(
                    e[0], e[1]) for e in condition.iteritems()
             ][0] for condition in self.get_conditions(data)]

    def get_conditions(self, data):
        rm = []
        for elem in data:
            if elem not in ['query', 'fields']:
                if elem not in self.model.get_fields_name():
                    rm.append(elem)
        for elem in rm:
            data.pop(elem)
        return [
            {k: v} for k, v in data.iteritems() if k not in ["query", "fields"]
            ]

    def paginate(self, data, **kwargs):
        """
        paginate the result of filter using ids limits.  Obviously, to
        work properly, you have to set the start to the last ids you
        receive from the last call on this method. The max number of
        row this method can give back depend on the paginate_by option.
        """

        where_query = self.build_conditions(data)
        args = []
        limit = kwargs.pop("end", None)
        if kwargs.get("start", None):
            where_query.append(" id >=?")
            args.append(kwargs.pop('start'))

        if len(where_query) > 0:
            data["query"] += " WHERE "
        data["query"] += " AND ".join(where_query)
        cursor = self.get_connector().cursor()

        # a hook for ordering
        data["query"] += " ORDER BY id ASC"

        if limit:
            data["query"] += " LIMIT {0}".format(limit)
        cursor.execute(data["query"].format(self.ressource_config['table']),
                       tuple(args)
                       )
        objs = []
        for elem in cursor.fetchall():
            objs.append(dict(zip(self.fields, elem)))
        return objs

    def get_fields(self, **fields):
        if self.partial:
            fields, kwargs = self.partial.get_partials(**fields)
            if not fields:
                fields = self.model.get_fields_name()
            for field in fields:
                if not field in self.model.get_fields_name():
                    raise BadRequest()
                if not self.model.pk_field.name in fields:
                    fields.append(self.model.pk_field.name)
        else:
            fields = self.model.get_fields_name()
        return fields

    def get_list(self, **kwargs):
        """
        return all the objects, paginated if needed, fitered if
        filters have been set.
        """
        self.fields = self.get_fields(**kwargs)
        fields = ", ".join(self.fields)
        kwargs["query"] = 'SELECT {0}'.format(fields)
        start = kwargs.pop("offset", None)
        end = kwargs.pop("count", None)
        data = self.filter(**kwargs)
        return self.paginate(data, start=start, end=end)

    def get(self, identifier):
        """
        Return a single row or raise NotFound
        """
        fields = ",".join(self.model.get_fields_name())
        query = "select {0} from {1} where {2}=?".format(
            fields,
            self.ressource_config["table"],
            self.model.pk_field.name)
        cursor = self.get_connector().cursor()
        cursor.execute(query, (identifier,))
        obj = cursor.fetchone()
        if obj:
            fields = self.model.get_fields_name()
            return dict(zip(fields, obj))
        else:
            raise NotFound

    def create(self, data):
        """
        Validate the data with :meth:`.base.DataStore.validate`
        And, if data is valid, create the row in database and return it.
        """
        self.validate(data)
        fields = []
        values = []
        for k, v in data.iteritems():
            if k in self.model.get_fields_name():
                fields.append(str(k))
                values.append(unicode(v))

        conn = self.get_connector()
        cursor = conn.cursor()

        query = "insert into {0} {1} values ({2})".format(
            self.ressource_config["table"],
            tuple(fields),
            ",".join(["?" for step in range(len(fields))])
            )
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def update(self, obj, data):
        """
        Retreive the object to be updated
        (:meth:`~.SQLiteDataStore.get` will raise a NotFound error if
        the row does not exist)

        Validate the fields to be updated and return the updated row
        """
        self.get(obj[self.model.pk_field.name])
        self.validate_fields(data)
        fields = []
        values = []
        for k, v in data.iteritems():
            if k in self.model.get_fields_name():
                fields.append(k)
                values.append(v)
        conn = self.get_connector()
        cursor = conn.cursor()
        update = " ,".join(["{0}='{1}'".format(f, v) for f, v in zip(fields,
                                                                    values)])
        query = "update {0} set {1} WHERE {2}={3}".format(
            self.ressource_config["table"],
            update,
            self.model.pk_field.name,
            obj[self.model.pk_field.name]
            )
        cursor.execute(query)
        conn.commit()
        conn.close()
        return self.get(obj[self.model.pk_field.name])

    def delete(self, identifier):
        """
        Retreive the object to be updated

        (:meth:`~.SQLiteDataStore.get` will raise a NotFound error if
        the row does not exist)

        Return None on success, Raise a 400 error if foreign key
        constrain prevent delete.

        """
        self.get(identifier)
        conn = self.get_connector()
        cursor = conn.cursor()

        query = "delete from {0} where {2}={1}".format(
            self.ressource_config["table"],
            identifier,
            self.model.pk_field.name)
        try:
            cursor.execute(query)
        except sqlite3.IntegrityError, e:
            message = ""
            if "foreign" in e.message:
                message = """another ressource depends on this
                object. Cloud not delete before all ressources
                depending on it are also deleted"""
            raise BadRequest(message)
        conn.commit()
        conn.close()

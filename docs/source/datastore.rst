

Datastore
=========

Datastores are the link between your API and a content provider. The
content provider can be a database, relational or not, a CSV file,
another API, well anything you can think of.

Using a Datastore
-----------------

The data your are using must be compatible with the datastore you want
to use. You cannot use a SQLDataStore with data coming from an api for
example.

Once the type of data and the datastore are compatible, you must:

* describe your ressource
* give the data to the datastore
* define optional options

Model: Describe your ressource
~~~~~~~~~~~~~~~~~~~~~~~

To describe your ressources, you must use a Model class. Model class
contain a list of field for each attribut of your ressource.

You can reuse existing fields or create new one based on existing
Fields.

Like each fields come with validators, you get validation for
free. You are also able to create new Fields just to add more
validators or change the one your Field class implement.

a simple Model can be something like:

.. code-block:: python

    class ApiModel(models.Model):

        fields = [models.IntegerField(name="age", required=True),
                  models.StringField(name="name", required=True),
                  models.PkField(name="id")
                  ]

Then you need the actual ressources. The format of the ressource
parameter depend on the datastore you use. For example, if you use the
SQLiteDataStore, ressource must be a dict containing the database name
and the database table used to store data:

.. code-block:: python

    ressource = {"name": "twitter.db", "table": "tweets"}

Finally you can give extra parameters to your DataStore like
pagination, authentication and so on. This will be done using the
options parameter.

The option parameter should contain pagination option, or whatever
your datastore may need:

.. code-block:: python

    options = {"paginated_by": 20}

You can then use your datastore :

.. code-block:: python

    datastore(ressource, model, **options)

To use datastore with your API you can just set parameters in the
Controller you use. The base controller take care of instanciate a
datastore for you. See the Controller documentation for more
informations about this.

Available DataStore
-------------------

Those datastore can be used immediately or beeing inherited to suit
your needs. They implements a complete datastore.

.. autoclass:: rest_api_framework.datastore.sql.SQLiteDataStore
  :members:

Create a DataStore
------------------

Creating a custom datastore is easy. You can override an existing
datastore or create on of you own .

A DataStore inherit from DataStore base class

.. autoclass:: rest_api_framework.datastore.base.DataStore
  :members:

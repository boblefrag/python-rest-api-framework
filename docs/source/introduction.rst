What is Python REST API Framework
=================================

Python REST API framework is a set of utilities based on werkzeug to
easily build Restful API. It keep a clean codebase and is easy to
configure and extends.

It does not decide how you want to render your data, or where they
lives, or other decisions.

Instead it give you a good start with an extensible architecture to
build your own API.

Python REST API Framework has not been create for the usual
case. Instead it give you some hook to your very special ressource
provider, your very special view management and your very special way
of displaying data.

Python REST API Framework is fully REST compilant; It implement the
common verbs:

* GET
* POST
* UPDATE
* DELETE

It also implement:

* PAGINATION
* AUTHENTICATION
* TROOTLING (comming soon)
* DATA VALIDATION
* ...

Architecture
------------

Python REST API Framework is base on the MVC pattern.

To create an API, you will need to create or reuse existing class:

Controller
~~~~~~~~~~

manage the routing of the urls. For a ressource, 2 urls are
created:

  * /ressource_name/ : this url will show a list of ressources
      (GET) or create new one (POST)

  * /ressource_name/identifier/ : this url will show a particular
      object (GET), update an existion object (PUT) or delete an
      existing object (DELETE)

Controller also check the authorized verbs. You can disable POST, PUT
and DELETE to make a read-only API for exemple.

If authentication is enabled, Controller call the
Authorisation/Authentication backend to manage user management

DataStore
~~~~~~~~~

Each method of a Controller call the DataStore to interact with
data. The DataStore must be able to retreive data from a
ressource.

Each datastore act on a particular type of ressource
(database backend, api backend, csv backend etc...). It must be
able to validate data, create new ressources, update existing
ressources, manage filters and pagination.

Optional configuration option, that can be unique for a particular
datastore make it very easy to configure, inherit and extend

Model
~~~~~

When you create a DataStoreInstance, you must feed it with a Model.
A Model is the python representation of a ressource object.

A Model will contain a list of Fields describing the ressource.

Field
~~~~~

Each fields of a Model must have a name to identify it. This name
correspond to the name of the field or property of the ressource.

Each Field can take optionals parameters to control its behavior. It
can also implment as many Validators than needed to control data integrity.

Validator
~~~~~~~~~

Each Validator implement the validate method. The validate method will
check a value and return True if the value is valide, False otherwise.

View
~~~~

Views defines how the data must be send to the client. It send a
Response object and set the needed headers, mime-type and other
presentation options


Authentication
~~~~~~~~~~~~~~

Authentication are class too. This mean that you can easily create
your own Authentication flow with REST API Framework.

Authentication Backend can use DataStore to get authentication and
authorization informations. As Backend can be anything from database
to other API, you do not need to store user informations on the same
machine or instance than your API.

It is moer secure, more scallable, easy to extend to suit your needs

How To use it
-------------

Python REST API framework is based on the MVC pattern. You define
Controllers, DataStore and Views. Each of them are based on backends
easily extendable and reusable.

Each of those part are totaly unrelated. You can use any controllers
with any datastore and any View

Datastore
~~~~~~~~~

First of all you have to decide where the data you want to expose
lies. It can be anything from a database, another API, even a list of
dictonary living in memory.

Depending on your data, you can reuse à datastore class or create a
new one to fit your needs. The datastore hanle the communication
between your API and the data

Controllers
~~~~~~~~~~~

The controller define your API. authorized verbs, pagination and
authentication. You will also need to describe your ressource to allow
validation on data.

Finaly you will need to hook your Controller to a Datastore. Once this is
done, your application is up and running.


QuickStart
----------

For this example, we will use a python list containing dicts. This is
our data:

.. code-block:: python

    ressources = [
        {"name": "bob",
        "age": a,
        "id": a
        } for a in range(100)
        ]

Then we have to describe this ressource. To describe a ressouce, you
must create a Model class inheriting from base Model class:

.. code-block:: python

   from rest_api_framework import models

   class ApiModel(models.Model):

       fields = [models.IntegerField(name="age", required=True),
                 models.StringField(name="name", required=True),
                 models.PkField(name="id")
                 ]


Each Field contain validators. When you reuse an existing Field class
you get his validators for free.

There is already a datastore to handle this type of data: PythonListDataStore.
We can reuse this store:

.. code-block:: python

    from rest_api_framework.datastore import PythonListDataStore

then we need a Controller class to hanlde our API:

.. code-block:: python

    from rest_api_framework.controllers import Controller

and a view to render our data

.. code-block:: python

    from rest_api_framework.views import JsonResponse


    class ApiApp(Controller):
        ressource = ressources
        ressource_name = "address"
        list_verbs = ["GET", "POST"]
        unique_verbs = ["GET", "PUT", "DElETE"]
        datastore = PythonListDataStore
        model = ApiModel
        options = {"paginated_by": 20}
        response_class = JsonResponse

* ressource : where the data lies. Each datastore implement his own
  way to gather data. For a PythonListDataStore, the actual python
  list is all we need.

* ressource_name: will be used to construct your urls

* list_verbs: the authorized verbs on the listing of your ressource. Here
  we authorize read and write

* unique_verbs: the authorized verbs on a ressource URI. Here we
  authorize read, deletion and modification.

* datastore: the datastore to be used

* model : The model defining your ressource schema
* options: here you can add optional configuration options like
  authentication, pagination etc...

* response_class: the class used to render your ressources. Here we
  use JsonResponse a naïve implementation of a json formater

To test you application locally, you can add:

.. code-block:: python

    if __name__ == '__main__':
        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([ApiApp])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

then type "python app.py" and your API is up and running


Using a database
~~~~~~~~~~~~~~~~

Instead of using a python dict, you may want to actualy save your data
in a database. To do so, you just have to change your datastore and
define your ressources in a way SQL datastore can understand.

SQLiteDataStore use sqlite3 as database backend. ressources will be a
dict with database name and table name. The rest of the configuration
is the same as with the PythonListDataStore.

.. note::

  if the database does not exist, REST API Framework create it for you

.. code-block:: python

    from rest_api_framework.datastore import SQLiteDataStore
    from rest_api_framework.controllers import Controller
    from rest_api_framework.views import JsonResponse
    from rest_api_framework import models

    class ApiModel(models.Model):
        fields = [models.StringField(name="message", required=True),
                  models.StringField(name="user", required=True),
                  models.PkField(name="id", required=True),
                  ]

    class ApiApp(Controller):
        ressource_name = "tweets"
        list_verbs = ["GET", "POST"]
        unique_verbs = ["GET", "PUT", "DElETE"]
        options = {
            "paginate_by": 20}

        datastore = SQLiteDataStore
        ressource = {"name": "twitter.db", "table": "tweets"}
        response_class = JsonResponse
        model = ApiModel

    if __name__ == '__main__':
        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([ApiApp])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True

Where to go from here
---------------------

* :doc:`Authentication and Authorization </authentication>`
* :doc:`multiple_endpoint`

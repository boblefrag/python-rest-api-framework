First Step Building a user endpoint
===================================

For this project we need users. Users will be helpfull for our adress
book and for our authentication process.

Users will be define with at least a first name and a last name. We
also need an unique identifier to retreive the user.

.. note::
   
   For this tutorial the file yyou create will be named app.py
   To launch your application then just type in a terminal:

   .. code-block:: bash
  
      python app.py

Define a model
~~~~~~~~~~~~~~

.. code-block:: python

    from rest_api_framework import models

    class UserModel(models.Model):

        fields = [models.StringField(name="first_name", required=True),
                  models.StringField(name="last_name", required=True),
                  models.PkField(name="id", required=True)
                  ]

The use of required_true will ensure that a user without this field
cannot be created

Chose a DataStore
~~~~~~~~~~~~~~~~~

We also need a datastore to get a place where we can save our
users. For instance we will use a sqlite3 database. The
SQLiteDataStore is what we need

.. code-block:: python

    from rest_api_framework.datastore import SQLiteDataStore

Chose a view
~~~~~~~~~~~~

We want results to be rendered as Json. We use the JsonResponse view
for that:

.. code-block:: python

    from rest_api_framework.views import JsonResponse

Create The user endpoint
~~~~~~~~~~~~~~~~~~~~~~~~

To create an endpoint, we need a controller. This will manage our
endpoint in a RESTFUL fashion.

.. code-block:: python

    from rest_api_framework.controllers import Controller

    class UserEndPoint(Controller):
        ressource = {
            "ressource_name": "users",
            "ressource": {"name": "adress_book.db", "table": "users"},
            "model": UserModel,
            "datastore": SQLiteDataStore
            }

        controller = {
            "list_verbs": ["GET", "POST"],
            "unique_verbs": ["GET", "PUT", "DElETE"]
            }

        view = {"response_class": JsonResponse}

then we must run our application:

.. code-block:: python

    if __name__ == '__main__':
        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([UserEndPoint])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

Summary
~~~~~~~

So far, all of the code should look like this:

.. code-block:: python

    from rest_api_framework import models
    from rest_api_framework.datastore import SQLiteDataStore
    from rest_api_framework.views import JsonResponse
    from rest_api_framework.controllers import Controller


    class UserModel(models.Model):

        fields = [models.StringField(name="first_name", required=True),
                  models.StringField(name="last_name", required=True),
                  models.PkField(name="id", required=True)
                  ]


    class UserEndPoint(Controller):
        ressource = {
            "ressource_name": "users",
            "ressource": {"name": "adress_book.db", "table": "users"},
            "model": UserModel,
            "datastore": SQLiteDataStore
            }

        controller = {
            "list_verbs": ["GET", "POST"],
            "unique_verbs": ["GET", "PUT", "DElETE"]
            }

        view = {"response_class": JsonResponse}

    if __name__ == '__main__':
        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([UserEndPoint])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)


.. note::

   to launch your application, just type in a terminal:

   .. code-block:: bash

      python app.py

Next: :doc:`using_user_endpoint`

.. Python Rest Api Framework documentation master file, created by
   sphinx-quickstart on Tue Oct  8 11:45:32 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python Rest Api Framework's documentation
=========================================

Python REST API framework is a set of utilities based on werkzeug to
easily build Restful API with a MVC pattern. Main features includes:
Pagination, Authentication, Authorization, Filters, Partials Response,
Error handling, data validators, data formaters...
and more...


Contents:

.. toctree::
   :maxdepth: 2

   introduction
   tutorial
   references
..   datastore
..   controller
..   pagination
..   authentication
..   multiple_endpoint



A Full working example
----------------------

.. code-block:: python

    from rest_api_framework import models
    from rest_api_framework.datastore import SQLiteDataStore
    from rest_api_framework.views import JsonResponse
    from rest_api_framework.controllers import Controller
    from rest_api_framework.datastore.validators import UniqueTogether
    from rest_api_framework.pagination import Pagination


    class UserModel(models.Model):
        """
        Define how to handle and validate your data.
        """
        fields = [models.StringField(name="first_name", required=True),
                  models.StringField(name="last_name", required=True),
                  models.PkField(name="id", required=True)
                  ]


    def remove_id(response, obj):
        """
        Do not show the id in the response.
        """
        obj.pop(response.model.pk_field.name)
        return obj


    class UserEndPoint(Controller):
        ressource = {
            "ressource_name": "users",
            "ressource": {"name": "adress_book.db", "table": "users"},
            "model": UserModel,
            "datastore": SQLiteDataStore,
            "options": {"validators": [UniqueTogether("first_name", "last_name")]}
            }

        controller = {
            "list_verbs": ["GET", "POST"],
            "unique_verbs": ["GET", "PUT", "DElETE"],
            "options": {"pagination": Pagination(20)}
            }

        view = {"response_class": JsonResponse,
                "options": {"formaters": ["add_ressource_uri", remove_id]}}


    if __name__ == '__main__':

        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([UserEndPoint])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

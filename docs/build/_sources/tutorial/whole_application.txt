The Whole Application
=====================

To let you have a look on the application you have build so far, here
is the whole application you have build:

.. code-block:: python

    from rest_api_framework import models
    from rest_api_framework.models.fields import ForeignKeyField
    from rest_api_framework.datastore import SQLiteDataStore, PythonListDataStore
    from rest_api_framework.datastore.validators import UniqueTogether
    from rest_api_framework.controllers import Controller
    from rest_api_framework.pagination import Pagination
    from rest_api_framework.authentication import (ApiKeyAuthentication,
                                                   Authorization)
    from rest_api_framework.ratelimit import RateLimit
    from rest_api_framework.partials import Partial
    from rest_api_framework.views import JsonResponse


    ressources = [{"accesskey": "hackme"}, {"accesskey": "nopassword"}]


    class KeyModel(models.Model):
        fields = [
            models.StringPkField(name="accesskey", required=True)
            ]


    class RateLimitModel(models.Model):
        fields = [models.StringPkField(name="access_key"),
                  models.IntegerField(name="quota"),
                  models.TimestampField(name="last_request")]


    datastore = PythonListDataStore(ressources, KeyModel)
    authentication = ApiKeyAuthentication(datastore, identifier="accesskey")


    class UserModel(models.Model):

        fields = [models.StringField(name="first_name", required=True),
                  models.StringField(name="last_name", required=True),
                  models.PkField(name="id", required=True),
                  models.IntForeign(name="address",
                                    foreign={"table": "address",
                                             "column": "id",
                                             }
                                    ),

                  ]


    class AddressModel(models.Model):

        fields = [models.StringField(name="country", required=True),
                  models.StringField(name="city", required=True),
                  models.StringField(name="street", required=True),
                  models.IntegerField(name="number", required=True),
                  models.PkField(name="id", required=True)
                  ]


    def remove_id(response, obj):
        obj.pop(response.model.pk_field.name)
        return obj


    def format_foreign_key(response, obj):

        for f in response.model.get_fields():
            if isinstance(f, ForeignKeyField):
                obj[f.name] = "/{0}/{1}/".format(f.options["foreign"]["table"],
                                                 obj[f.name])
        return obj


    def foreign_keys_format(view, obj):
        for f in view.datastore.model.get_fields():
            if isinstance(f, ForeignKeyField):
                if obj.get(f.name):
                    obj[f.name] = int(obj[f.name].split("/")[-2])
        return obj


    class UserEndPoint(Controller):
        ressource = {
            "ressource_name": "users",
            "ressource": {"name": "adress_book.db", "table": "users"},
            "model": UserModel,
            "datastore": SQLiteDataStore,
            "options": {"validators": [UniqueTogether("first_name", "last_name")],
                        }
            }

        controller = {
            "list_verbs": ["GET", "POST"],
            "unique_verbs": ["GET", "PUT", "DElETE"],
            "options": {"pagination": Pagination(20),
                        "formaters": [foreign_keys_format],
                        "authentication": authentication,
                        "authorization": Authorization,
                        "ratelimit": RateLimit(
                    PythonListDataStore([],RateLimitModel),
                    interval=100,
                    quota=200),
                        }
            }

        view = {"response_class": JsonResponse,
                "options": {"formaters": ["add_ressource_uri",
                                          remove_id,
                                          format_foreign_key
                                          ]}}


    class AddressEndPoint(UserEndPoint):
        ressource = {
            "ressource_name": "address",
            "ressource": {"name": "adress_book.db", "table": "address"},
            "model": AddressModel,
            "datastore": SQLiteDataStore,
            "options": {"partial": Partial()}
            }
    if __name__ == '__main__':

        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([AddressEndPoint, UserEndPoint])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

"""
An app to test how to make API services with werkzeug

How it should work:

- describe your ressources
  - fields to be displayed
  - how fields should be displayed
  - etc...

- define global settings

  - pagination
  - authorization
  - authentication
  - throttling
  - etc..

"""
import sys
sys.path.append("..")

from rest_api_framework.datastore import PythonListDataStore, SQLiteDataStore
from rest_api_framework import models
from rest_api_framework.pagination import Pagination
from rest_api_framework.controllers import Controller, WSGIDispatcher
from rest_api_framework.views import JsonResponse


ressources = [
    {"name": "bob",
     "age": a,
     "id": a
     } for a in range(100)
    ]

api_keys = [
    {"id": "azerty"},
    {"id": "querty"}
    ]


class ApiModel(models.Model):
    fields = [models.IntegerField(name="age", required=True),
              models.StringField(name="name", required=True),
              models.PkField(name="id")
              ]


class ApiApp(Controller):
    ressource = {
        "ressource_name": "address",
        "ressource": ressources,
        "model": ApiModel,
        "datastore": PythonListDataStore
        }

    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DELETE"],
        "options": {"pagination": Pagination(20)}
        }

    view = {"response_class": JsonResponse}


class SQLiteApp(Controller):
    ressource = {
        "ressource_name": "address",
        "ressource": {"name": ":memory:", "table": "address"},
        "model": ApiModel,
        "datastore": SQLiteDataStore
        }

    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DELETE"],
        "options": {"pagination": Pagination(20)}
        }

    view = {"response_class": JsonResponse}


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = WSGIDispatcher([SQLiteApp])
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

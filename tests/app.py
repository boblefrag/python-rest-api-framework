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
from rest_api_framework.datastore import PythonListDataStore
from rest_api_framework import models
from rest_api_framework.controllers import Controller
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

    ressource_name = "address"
    list_verbs = ["GET", "POST"]
    unique_verbs = ["GET", "PUT", "DElETE"]
    options = {
        "paginate_by": 20}

    model = ApiModel
    datastore = PythonListDataStore
    ressource = ressources
    response_class = JsonResponse

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = ApiApp()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

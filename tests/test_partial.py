from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
import json
from rest_api_framework.controllers import WSGIDispatcher
from rest_api_framework.datastore import PythonListDataStore, SQLiteDataStore
from rest_api_framework.partials import Partial
from rest_api_framework import models
from app import ApiApp, SQLiteApp
import os

ressources = [
    {"name": "bob",
     "age": a,
     "id": a
     } for a in range(100)
    ]


class ApiModel(models.Model):
    fields = [
        models.StringPkField(name="id", required=True)
        ]


class SQLModel(models.Model):

    fields = [models.IntegerField(name="age", required=True),
              models.StringField(name="name", required=True),
              models.PkField(name="id")
              ]


class PartialApiApp(ApiApp):

    ressource = {
        "ressource_name": "address",
        "ressource": ressources,
        "model": ApiModel,
        "datastore": PythonListDataStore,
        "options": {"partial": Partial()}
        }


class PartialSQLApp(SQLiteApp):
    ressource = {
        "ressource_name": "address",
        "ressource": {"name": "test.db", "table": "address"},
        "model": SQLModel,
        "datastore": SQLiteDataStore,
        "options": {"partial": Partial()}
        }


class TestPartialResponse(TestCase):

    def test_get_partial_list(self):
        client = Client(WSGIDispatcher([PartialApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/?fields=age")
        # we only want "age". get_list add id, JsonResponse add ressource_uri
        self.assertEqual(len(json.loads(resp.data)["object_list"][0].keys()), 3)

    def test_get_partial_raise(self):
        client = Client(WSGIDispatcher([PartialApiApp]),
                        response_wrapper=BaseResponse)
        response = client.get("/address/?fields=wrongkey")
        self.assertEqual(response.status_code, 400)


class TestPartialSQLResponse(TestCase):
    def test_get_partial_sql(self):
        client = Client(WSGIDispatcher([PartialSQLApp]),
                        response_wrapper=BaseResponse)
        for i in range(100):
            client.post("/address/",
                        data=json.dumps({"name": "bob", "age": 34}))

        resp = client.get("/address/?fields=age")
        # we only want "age". get_list add id, JsonResponse add ressource_uri
        self.assertEqual(len(json.loads(resp.data)["object_list"][0].keys()), 3)
        os.remove("test.db")

    def test_get_partial_sql_raise(self):
        client = Client(WSGIDispatcher([PartialSQLApp]),
                        response_wrapper=BaseResponse)
        for i in range(100):
            client.post("/address/",
                        data=json.dumps({"name": "bob", "age": 34}))
        response = client.get("/address/?fields=wrongkey")
        self.assertEqual(response.status_code, 400)
        os.remove("test.db")

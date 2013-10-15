from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from app import ApiApp, SQLiteApp
import json
import datetime
from rest_api_framework.authentication import (ApiKeyAuthorization,
                                               ApiKeyAuthentication)
from rest_api_framework.datastore import PythonListDataStore, SQLiteDataStore
from rest_api_framework import models
from rest_api_framework.controllers import WSGIDispatcher
from rest_api_framework.partials import Partial
from rest_api_framework.ratelimit import RateLimit
import time
import os


class ApiModel(models.Model):
    fields = [
        models.StringPkField(name="id", required=True)
        ]


class SQLModel(models.Model):

    fields = [models.IntegerField(name="age", required=True),
              models.StringField(name="name", required=True),
              models.PkField(name="id")
              ]


ressources = [
    {"name": "bob",
     "age": a,
     "id": a
     } for a in range(100)
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


def controller_formater(view, data):
    print view.datastore.model
    data["age"] = int(data["age"])
    return data


class FormatedApp(ApiApp):
    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DElETE"],
        "options": {"formaters": [controller_formater,
                                  ]
                    }
        }


class TestApiView(TestCase):

    def test_get_list(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(json.loads(resp.data)["object_list"], list)

    def test_get(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/1/")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/400/")
        self.assertEqual(resp.status_code, 404)

    def test_create(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.post("/address/",
                           data=json.dumps({'name': 'bob', 'age': 34}))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.headers['Location'],
                         "http://localhost/address/100/")
        resp = client.post("/address/",
                           data={"test": datetime.datetime.now()})
        self.assertEqual(resp.status_code, 400)

    def test_updated(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.put("/address/1/",
                          data=json.dumps({'name': 'boby mc queen'}))
        self.assertEqual(resp.status_code, 200)

    def test_delete(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.delete("/address/4/")
        self.assertEqual(resp.status_code, 200)


class TestAuthentication(TestCase):

    def test_unauth_get_list(self):
        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DElETE"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }

        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)
        resp = client.get("/address/")
        self.assertEqual(resp.status_code, 401)

    def test_auth_get_list(self):
        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DElETE"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }

        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)
        resp = client.get("/address/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/address/?apikey=querty")
        self.assertEqual(resp.status_code, 401)

    def test_auth_unique_uri(self):
        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DElETE"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }

        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)

        resp = client.get("/address/1/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/address/1/?apikey=querty")
        self.assertEqual(resp.status_code, 401)

    def test_post_auth(self):
        """
        Test a read only api.
        GET should be ok, POST and PUT should not
        """

        from rest_api_framework.pagination import Pagination
        ressources = [{"id": "azerty"}]
        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET"],
                "unique_verbs": ["GET"],
                "options": {"pagination": Pagination(20),
                            "authentication": authentication,
                            "authorization": ApiKeyAuthorization
                            }
                }
        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)

        resp = client.get("/address/1/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.post("/address/?apikey=azerty",
                           data=json.dumps({'name': 'bob', 'age': 34}))
        self.assertEqual(resp.status_code, 405)

    def test_badlyconfigured_api(self):

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET"],
                "unique_verbs": ["GET"],
                "options": {"authorization": ApiKeyAuthorization}
                }
        self.assertRaises(ValueError, ApiAppAuth, "")


class TestPagination(TestCase):

    def test_base_pagination(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/")

        self.assertEqual(len(json.loads(resp.data)["object_list"]), 20)

    def test_base_pagination_count(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/?count=2")
        self.assertEqual(len(json.loads(resp.data)), 2)

    def test_base_pagination_count_overflow(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/?count=200")
        self.assertEqual(len(json.loads(resp.data)["object_list"]), 20)

    def test_base_pagination_offset(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/?offset=2")
        self.assertEqual(json.loads(resp.data)["object_list"][0]['ressource_uri'],
                         "/address/2/")


class TestSQlitePagination(TestCase):

    def test_base_pagination(self):
        client = Client(WSGIDispatcher([SQLiteApp]),
                        response_wrapper=BaseResponse)
        for i in range(100):
            client.post("/address/",
                        data=json.dumps({"name": "bob", "age": 34}))
        resp = client.get("/address/")
        self.assertEqual(len(json.loads(resp.data)["object_list"]), 20)
        os.remove("test.db")

    def test_base_pagination_offset(self):
        client = Client(WSGIDispatcher([SQLiteApp]),
                        response_wrapper=BaseResponse)
        for i in range(100):
            client.post("/address/",
                        data=json.dumps({"name": "bob", "age": 34}))
        resp = client.get("/address/?offset=2")
        self.assertEqual(json.loads(resp.data)["object_list"][0]['id'], 2)
        os.remove("test.db")

    def test_base_pagination_count(self):
        client = Client(WSGIDispatcher([SQLiteApp]),
                        response_wrapper=BaseResponse)
        for i in range(100):
            client.post("/address/",
                        data=json.dumps({"name": "bob", "age": 34}))
        resp = client.get("/address/?count=2")
        self.assertEqual(len(json.loads(resp.data)), 2)
        os.remove("test.db")

    def test_base_pagination_count_offset(self):
        client = Client(WSGIDispatcher([SQLiteApp]),
                        response_wrapper=BaseResponse)
        for i in range(100):
            client.post("/address/",
                        data=json.dumps({"name": "bob", "age": 34}))
        resp = client.get("/address/?count=2&offset=4")
        self.assertEqual(len(json.loads(resp.data)), 2)
        self.assertEqual(json.loads(resp.data)["object_list"][0]['id'], 4)
        os.remove("test.db")


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


class TestRateLimit(TestCase):

    def test_ratelimit(self):

        ressources = [{"id": "azerty"}]
        ratelimit_ressources = [{"id": "azerty"}]

        class RateLimitModel(models.Model):
            fields = [models.StringPkField(name="id"),
                      models.IntegerField(name="quota"),
                      models.TimestampField(name="last_request")]

        authentication = ApiKeyAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class RateLimitApiApp(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DElETE"],
                "options": {"authentication": authentication,
                            "ratelimit": RateLimit(PythonListDataStore(
                            ratelimit_ressources, RateLimitModel),
                                                   interval=1,
                                                   quota=2)
                            }
                }

        client = Client(
            WSGIDispatcher([RateLimitApiApp]),
            response_wrapper=BaseResponse)
        resp = client.get("/address/")
        self.assertEqual(resp.status_code, 401)
        resp = client.get("/address/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/address/?apikey=azerty")
        self.assertEqual(resp.status_code, 429)
        time.sleep(1)
        resp = client.get("/address/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)


class TestControllerFormaters(TestCase):

    def test_create(self):
        client = Client(WSGIDispatcher([FormatedApp]),
                        response_wrapper=BaseResponse)
        resp = client.post("/address/",
                           data=json.dumps({'name': 'bob', 'age': "34"}))
        self.assertEqual(resp.status_code, 201)

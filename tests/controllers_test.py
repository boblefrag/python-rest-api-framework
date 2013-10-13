from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from app import ApiApp, SQLiteApp
import json
import datetime
from rest_api_framework.authentication import (ApiKeyAuthorization,
                                               ApiKeyAuthentication)
from rest_api_framework.datastore import PythonListDataStore
from rest_api_framework import models
from rest_api_framework.controllers import WSGIDispatcher
import os


class ApiModel(models.Model):
    fields = [
        models.StringField(name="id", required=True)
        ]


class TestApiView(TestCase):

    def test_get_list(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(json.loads(resp.data), list)

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
                         "http://localhost/address/100")
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


class TestPagination(TestCase):

    def test_base_pagination(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/")
        self.assertEqual(len(json.loads(resp.data)), 20)

    def test_base_pagination_count(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/?count=2")
        self.assertEqual(len(json.loads(resp.data)), 2)

    def test_base_pagination_count_overflow(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/?count=200")
        self.assertEqual(len(json.loads(resp.data)), 20)

    def test_base_pagination_offset(self):
        client = Client(WSGIDispatcher([ApiApp]),
                        response_wrapper=BaseResponse)
        resp = client.get("/address/?offset=2")
        self.assertEqual(json.loads(resp.data)[0]['id'], 2)


class TestSQlitePagination(TestCase):

    def test_base_pagination(self):
        client = Client(WSGIDispatcher([SQLiteApp]),
                        response_wrapper=BaseResponse)
        for i in range(100):
            client.post("/address/",
                        data=json.dumps({"name": "bob", "age": 34}))
        resp = client.get("/address/")
        self.assertEqual(len(json.loads(resp.data)), 20)
        os.remove("test.db")

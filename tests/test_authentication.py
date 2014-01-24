from unittest import TestCase
import json

from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from werkzeug import Headers

from app import ApiApp
from rest_api_framework.authentication import (ApiKeyAuthorization,
                                               Authorization,
                                               ApiKeyAuthentication,
                                               BasicAuthentication)
from rest_api_framework.datastore import PythonListDataStore
from rest_api_framework import models
from rest_api_framework.controllers import WSGIDispatcher


class ApiModel(models.Model):
    fields = [
        models.StringPkField(name="id", required=True)
        ]


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


class TestBasicAuth(TestCase):
    def test_basic_auth(self):
        from base64 import b64encode

        class BasicModel(models.Model):
            fields = [
                models.StringPkField(name="user", required=True),
                models.StringField(name="password", required=True)
                ]
        ressources = [{"user": "login",
                       "password": "pass"}]
        authentication = BasicAuthentication(
            PythonListDataStore(ressources,
                                ApiModel)
            )

        class ApiAppAuth(ApiApp):
            controller = {
                "list_verbs": ["GET"],
                "unique_verbs": ["GET"],
                "options": {"authentication": authentication,
                            "authorization": Authorization
                            }
                }
        client = Client(
            WSGIDispatcher([ApiAppAuth]),
            response_wrapper=BaseResponse)
        credentials = b64encode("login:pass")
        headers = Headers([('Authorization: Basic', credentials)])

        resp = client.get("/address/1/", headers=headers)
        self.assertEqual(resp.status_code, 200)

        credentials = b64encode("login:hackme")
        headers = Headers([('Authorization: Basic', credentials)])
        resp = client.get("/address/1/", headers=headers)
        self.assertEqual(resp.status_code, 401)

        resp = client.get("/address/1/")
        self.assertEqual(resp.status_code, 401)

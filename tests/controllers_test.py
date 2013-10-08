from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from app import ApiApp
import json
import datetime
from rest_api_framework.authentication import ApiKeyAuth
from rest_api_framework.datastore import PythonListDataStore


class TestApiView(TestCase):

    def test_get_list(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(json.loads(resp.data), list)

    def test_get(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.get("/1/")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/400/")
        self.assertEqual(resp.status_code, 404)

    def test_create(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.post("/", data=json.dumps({'name': 'bob', 'age': 34}))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.headers['Location'], "http://localhost/100")
        resp = client.post("/", data={"test": datetime.datetime.now()})
        self.assertEqual(resp.status_code, 400)

    def test_updated(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.put("/1/", data=json.dumps({'name': 'boby mc queen'}))
        self.assertEqual(resp.status_code, 200)

    def test_delete(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.delete("/4/")
        self.assertEqual(resp.status_code, 200)


class TestAuthentication(TestCase):

    def test_unauth_get_list(self):
        ressources = [{"id": "azerty"}]
        description = {"id": {"type": basestring, "required": True}}
        client = Client(
            ApiApp(
                authentication=ApiKeyAuth(
                    PythonListDataStore(ressources,
                                        description=description)
                    )
                ),
            response_wrapper=BaseResponse)
        resp = client.get("/")
        self.assertEqual(resp.status_code, 401)

    def test_auth_get_list(self):
        ressources = [{"id": "azerty"}]
        description = {"id": {"type": basestring, "required": True}}
        client = Client(
            ApiApp(
                authentication=ApiKeyAuth(
                    PythonListDataStore(ressources,
                                        description=description)
                    )
                ),
            response_wrapper=BaseResponse)
        resp = client.get("/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/?apikey=querty")
        self.assertEqual(resp.status_code, 401)

    def test_auth_unique_uri(self):
        ressources = [{"id": "azerty"}]
        description = {"id": {"type": basestring, "required": True}}
        client = Client(
            ApiApp(
                authentication=ApiKeyAuth(
                    PythonListDataStore(ressources,
                                        description=description)
                    )
                ),
            response_wrapper=BaseResponse)
        resp = client.get("/1/?apikey=azerty")
        self.assertEqual(resp.status_code, 200)
        resp = client.get("/1/?apikey=querty")
        self.assertEqual(resp.status_code, 401)

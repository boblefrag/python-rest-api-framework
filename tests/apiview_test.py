from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from rest_api_framework.app import ApiApp
import json


class TestApiView(TestCase):

    def test_get_list(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)

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
        resp = client.post("/", data=json.dumps({"hello": "world"}))
        self.assertEqual(resp.status_code, 400)

    def test_updated(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.put("/1/", data=json.dumps({'name': 'boby mc queen'}))
        self.assertEqual(resp.status_code, 200)

    def test_delete(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.delete("/4/")
        self.assertEqual(resp.status_code, 200)

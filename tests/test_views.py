from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from app import ApiApp
import json
import datetime
from rest_api_framework.controllers import WSGIDispatcher


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
                         "http://localhost/address/101/")
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

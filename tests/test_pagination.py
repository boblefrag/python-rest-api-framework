from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from app import ApiApp, SQLiteApp
import json
from rest_api_framework.controllers import WSGIDispatcher
import os


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

from unittest import TestCase
from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from rest_api_framework.app import ApiApp


class TestApiView(TestCase):

    def test_get(self):
        client = Client(ApiApp(), response_wrapper=BaseResponse)
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)

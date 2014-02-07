from unittest import TestCase
import json
import time

from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client

from app import ApiApp
from rest_api_framework.authentication import ApiKeyAuthentication
from rest_api_framework.datastore import PythonListDataStore
from rest_api_framework import models
from rest_api_framework.controllers import WSGIDispatcher
from rest_api_framework.ratelimit import RateLimit


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


ratelimit_ressources = [{"id": "azerty"}]


class RateLimitModel(models.Model):
    fields = [models.StringPkField(name="id"),
              models.IntegerField(name="quota"),
              models.TimestampField(name="last_request")]

authentication = ApiKeyAuthentication(
    PythonListDataStore(ratelimit_ressources,
                        ApiModel)
    )


class RateLimitApiApp(ApiApp):
    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DELETE"],
        "options": {"authentication": authentication,
                    "ratelimit":
                    RateLimit(
                        PythonListDataStore(ratelimit_ressources,
                                            RateLimitModel),
                        interval=1, quota=2)
                    }
        }


def controller_formater(view, data):
    data["age"] = int(data["age"])
    return data


class FormatedApp(ApiApp):
    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DELETE"],
        "options": {"formaters": [controller_formater,
                                  ]
                    }
        }


class TestRateLimit(TestCase):
    def test_ratelimit(self):
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

    def test_unconfigured_rate_limit(self):
        class BadConfRateLimitApiApp(ApiApp):
            controller = {
                "list_verbs": ["GET", "POST"],
                "unique_verbs": ["GET", "PUT", "DELETE"],
                "options": {"ratelimit": RateLimit(
                    PythonListDataStore(ratelimit_ressources, RateLimitModel),
                    interval=1, quota=2)}
                }

        self.assertRaises(ValueError,
                          WSGIDispatcher,
                          [BadConfRateLimitApiApp],
                          )


class TestControllerFormaters(TestCase):

    def test_create(self):
        client = Client(WSGIDispatcher([FormatedApp]),
                        response_wrapper=BaseResponse)
        resp = client.post("/address/",
                           data=json.dumps({'name': 'bob', 'age': "34"}))

        self.assertEqual(resp.status_code, 201)


class TestSayHello(TestCase):

    def test_say_hello(self):
        client = Client(WSGIDispatcher([FormatedApp]),
                        response_wrapper=BaseResponse)
        resp = client.get('/')
        print dir(resp), resp.data
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            {"version": "devel", "name": "PRAF"},
            json.loads(resp.data)
            )

from unittest import TestCase
import json
import os

from werkzeug.wrappers import BaseResponse
from werkzeug.test import Client
from rxjson import Rx

from rest_api_framework.controllers import WSGIDispatcher
from .app import ApiApp

HERE = os.path.dirname(os.path.abspath(__file__))


class TestSpore(TestCase):

    def test_spore(self):
        client = Client(WSGIDispatcher([ApiApp], name='ApiApp', version='1.0',
                                       base_url='http://apiapp.com'),
                        response_wrapper=BaseResponse)
        resp = client.get("/spore/")

        self.assertEqual(resp.status_code, 200)
        spore = json.loads(resp.data)

        # basic fields
        self.assertEqual(spore['name'], 'ApiApp')
        self.assertEqual(spore['base_url'], 'http://apiapp.com')
        self.assertEqual(spore['version'], '1.0')

        # methods
        self.assertIn('get_address_unique_uri', spore['methods'])
        self.assertEqual('/address/:identifier/',
                         spore['methods']['get_address_unique_uri']['path'])
        self.assertIn(
            'identifier',
            spore['methods']['get_address_unique_uri']['required_params'])

    def test_rxjson_spore(self):
        rx = Rx.Factory({'register_core_types': True})
        client = Client(WSGIDispatcher([ApiApp], name='ApiApp', version='1.0',
                                       base_url='http://apiapp.com'),
                        response_wrapper=BaseResponse)
        resp = client.get("/spore/")

        with open(os.path.join(HERE, 'spore_validation.rx')) as f:
            spore_json_schema = json.loads(f.read())
            spore_schema = rx.make_schema(spore_json_schema)
            self.assertTrue(spore_schema.check(json.loads(resp.data)))

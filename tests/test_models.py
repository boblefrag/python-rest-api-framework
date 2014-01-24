from unittest import TestCase
from rest_api_framework import models


class ApiModel(models.Model):
    fields = [models.IntegerField(name="age", required=True),
              models.StringField(name="name", required=True),
              models.PkField(name="id")
              ]


class TestSchema(TestCase):
    def test_pk_schema(self):
        model = ApiModel()
        self.assertEqual(model.get_schema(), {
            'age': {
                'required': 'true',
                'type': 'integer',
                'example': 42
            }, 'name': {
                'required': 'true',
                'type': 'string',
                'example': 'Hello World'}})

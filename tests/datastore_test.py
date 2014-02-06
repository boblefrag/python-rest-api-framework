from unittest import TestCase
import os

from werkzeug.exceptions import BadRequest, NotFound

from rest_api_framework.datastore import (PythonListDataStore,
                                          SQLiteDataStore)
from rest_api_framework import models


class ApiModel(models.Model):
    fields = [models.IntegerField(name="age", required=True),
              models.StringField(name="name", required=True),
              models.PkField(name="id")
              ]


class UserModel(models.Model):
    fields = [models.StringField(name="first_name", required=True),
              models.StringField(name="last_name", required=True),
              models.PkField(name="id"),
              models.IntForeign(name="address",
                                foreign={"table": "address",
                                         "column": "id"})
              ]


class ModelTest(TestCase):
    def test_badlyconfigured_model(self):
        class BadModel(models.Model):
            fields = [models.IntegerField(name="age", required=True),
                      models.StringField(name="name", required=True),
                      ]

        self.assertRaises(ValueError, BadModel)

    def test_unfound_field(self):
        model = ApiModel()
        self.assertEqual(model.get_field("something"), None)


class PythonListDataStoreTest(TestCase):
    def test_validator(self):
        from rest_api_framework.datastore.validators import UniqueTogether

        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(
            data_list,
            ApiModel,
            validators=[UniqueTogether("age", "name")]
            )

        self.assertEqual(store.validate({"name": "bob", "age": 209}), None)
        self.assertRaises(BadRequest,
                          store.validate,
                          {"name": "bob", "age": 20})

        self.assertRaises(
            BadRequest,
            store.update,
            {"name": "bob", "age": 34, "id": 34},
            {"age": 20})

        store = SQLiteDataStore(
            {"name": ":memory:", "table": "address"},
            ApiModel,
            validators=[UniqueTogether("age", "name")]
            )

        for i in range(100):
            store.create({"name": "bob", "age": i+1})

        self.assertEqual(store.validate({"name": "bob", "age": 209}), None)
        self.assertRaises(BadRequest,
                          store.validate,
                          {"name": "bob", "age": 20})

    def test_validation(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, ApiModel)

        self.assertEqual(store.validate({"name": "bob", "age": 34}), None)
        self.assertRaises(BadRequest, store.validate, "a test")
        self.assertRaises(BadRequest,
                          store.validate,
                          {"name": "bob", "age": "34"})
        self.assertRaises(BadRequest,
                          store.validate_fields,
                          {"age": "34"})
        self.assertRaises(BadRequest,
                          store.validate_fields,
                          "age")
        data_list = []

        class OtherModel(models.Model):
            fields = [models.TimestampField(name="timestamp",
                                                 required=True),
                      models.PkField(name="id")
                      ]

        store = PythonListDataStore(data_list, OtherModel)
        self.assertRaises(BadRequest,
                          store.validate_fields,
                          {"timestamp": 2345})

    def test_pagination(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, ApiModel, paginate_by=10)
        self.assertEqual(len(store.paginate(data_list, 0, 10)), 10)
        self.assertEqual(store.paginate(data_list, 10, None)[0]["id"], 10)
        self.assertEqual(store.paginate(data_list, 0, 15)[-1]["id"], 14)

    def test_get(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]
        store = PythonListDataStore(data_list, ApiModel)
        self.assertEqual(store.get(10)["id"], 10)
        self.assertRaises(NotFound,
                          store.get,
                          100)

    def test_create(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, ApiModel)
        # The object does not exists
        self.assertRaises(NotFound,
                          store.get,
                          100)
        # The object is created
        self.assertEqual(store.create({"name": "bob", "age": 34}), 100)
        # The object exists
        self.assertEqual(store.get(100)["id"], 100)
        self.assertRaises(BadRequest,
                          store.create,
                          {"name": "bob", "age": "34"})

    def test_update(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, ApiModel)
        self.assertEqual(
            store.update(
                {"name": "bob", "age": "34", "id": 34},
                {"name": "boby mc gee"}
                ), {"name": "boby mc gee", "age": "34", "id": 34})
        # adress is not part of the ressource description, it should
        # raise
        self.assertRaises(BadRequest,
                          store.update,
                          {"name": "bob", "age": "35", "id": 35},
                          {"adress": "1, main street"}
                          )

        self.assertRaises(NotFound,
                          store.update,
                          {"name": "bob", "age": "100", "id": 100},
                          {"name": "boby mc gee"}
                          )

    def test_delete(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, ApiModel)
        # the object exists
        self.assertEqual(store.get(10)["id"], 10)
        # is delete
        self.assertEqual(store.delete(10), None)
        # does not exist anymore
        self.assertRaises(NotFound,
                          store.get,
                          10)

    def test_filter(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, ApiModel)
        self.assertEqual(len(store.filter(age=24)), 1)
        self.assertEqual(len(store.filter(name="bob")), 100)
        self.assertEqual(len(store.filter(name="john")), 0)
        self.assertEqual(len(store.filter(name="bob", age=12)), 1)


class SQLiteDataStoreTest(TestCase):
    def test_validation(self):
        store = SQLiteDataStore(
            {"name": ":memory:", "table": "address"},
            ApiModel)

        self.assertEqual(store.validate({"name": "bob", "age": 34}), None)
        self.assertRaises(BadRequest, store.validate, "a test")
        self.assertRaises(BadRequest,
                          store.validate,
                          {"name": "bob", "age": "34"})
        self.assertRaises(BadRequest,
                          store.validate,
                          {"name": 54, "age": 34})
        self.assertRaises(BadRequest,
                          store.validate_fields,
                          {"age": "34"})
        self.assertRaises(BadRequest,
                          store.validate_fields,
                          "age")

    def test_pagination(self):
        store = SQLiteDataStore(
            {"name": ":memory:", "table": "address"},
            ApiModel)

        for i in range(100):
            store.create({"name": "bob", "age": 34})

        self.assertEqual(len(store.get_list(count=10)), 10)
        self.assertEqual(store.get_list(count=10)[-1]["id"], 10)
        self.assertEqual(store.get_list(offset=15)[0]["id"], 15)

        req = store.get_list(offset=15, count=2)

        self.assertEqual(len(req), 2)
        self.assertEqual(req[0]['id'], 15)

    def test_get(self):
        store = SQLiteDataStore(
            {"name": ":memory:", "table": "address"}, ApiModel)

        for i in range(100):
            store.create({"name": "bob", "age": 34})

        self.assertEqual(store.get(10)["id"], 10)
        self.assertRaises(NotFound,
                          store.get,
                          101)

    def test_create(self):
        data = {"name": ":memory:", "table": "address"}
        store = SQLiteDataStore(
            data,
            ApiModel)

        self.assertRaises(NotFound,
                          store.get,
                          1)
        self.assertEqual(store.create({"name": "bob", "age": 34}), 1)
        self.assertEqual(store.create({"name": "bob", "age": 35}), 2)
        self.assertEqual(store.create({"name": "bob", "age": 34}), 3)
        self.assertEqual(store.get(3)["id"], 3)

    def test_foreign_keys(self):
        data = {"name": "test.db", "table": "address"}
        store = SQLiteDataStore(
            data,
            ApiModel)
        self.assertEqual(store.create({"name": "bob", "age": 34}), 1)

        data = {"name": "test.db", "table": "user"}
        store2 = SQLiteDataStore(
            data,
            UserModel)
        self.assertEqual(store2.create({"last_name": "bob",
                                       "first_name": "Dick",
                                       "address": 1}), 1)

        self.assertRaises(BadRequest,
                          store2.create,
                          {"last_name": "moby",
                           "first_name": "Dick",
                           "address": 2}
                          )
        self.assertRaises(BadRequest, store.delete, 1)
        os.remove("test.db")

    def test_update(self):
        store = SQLiteDataStore(
            {"name": ":memory:", "table": "address"},
            ApiModel)

        for i in range(100):
            store.create({"name": "bob", "age": 34})

        self.assertEqual(
            store.update(
                {"name": "bob", "age": 34, "id": 34},
                {"name": "boby mc gee"}
                ), {"name": "boby mc gee", "age": 34, "id": 34})

        self.assertEqual(
            store.update(
                {"name": "bob", "age": 35, "id": 35},
                {"name": "boby mc gee", "age": 67}
                ), {"name": "boby mc gee", "age": 67, "id": 35})

        # adress is not part of the ressource description, it should
        # raise
        self.assertRaises(BadRequest,
                          store.update,
                          {"name": "bob", "age": "35", "id": 35},
                          {"adress": "1, main street"}
                          )

        self.assertRaises(NotFound,
                          store.update,
                          {"name": "bob", "age": "100", "id": 400},
                          {"name": "boby mc gee"}
                          )

    def test_delete(self):
        store = SQLiteDataStore(
            {"name": ":memory:", "table": "address"}, ApiModel)

        for i in range(100):
            store.create({"name": "bob", "age": 34})

        # the object exists
        self.assertEqual(store.get(10)["id"], 10)

        # is delete
        self.assertEqual(store.delete(10), None)

        # does not exist anymore
        self.assertRaises(NotFound,
                          store.get,
                          10)

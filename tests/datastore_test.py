from unittest import TestCase
from rest_api_framework.datastore import (PythonListDataStore,
                                          SQLiteDataStore)
#                                          ApiDataStore)
from rest_api_framework import models

from werkzeug.exceptions import BadRequest, NotFound
import os


class ApiModel(models.Model):

    fields = [models.IntegerField(name="age", required=True),
              models.StringField(name="name", required=True),
              models.PkField(name="id")
              ]


class PythonListDataStoreTest(TestCase):

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

    def test_pagination(self):
        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, ApiModel, paginate_by=10)
        self.assertEqual(len(store.paginate(data_list)), 10)
        self.assertEqual(store.paginate(data_list, start=10)[0]["id"], 10)
        self.assertEqual(store.paginate(data_list, end=15)[-1]["id"], 14)

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
                ),{"name": "boby mc gee", "age": "34", "id": 34})
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
            {"name": "test.db", "table": "address"},
            ApiModel)
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
        os.remove("test.db")

    def test_pagination(self):
        store = SQLiteDataStore(
            {"name": "test.db", "table": "address"},
            ApiModel,
            paginate_by=10)
        for i in range(100):
            store.create({"name": "bob", "age": 34})
        self.assertEqual(len(store.get_list()), 10)
        self.assertEqual(store.get_list(start=10)[0]["id"], 10)
        self.assertEqual(store.get_list(end=15)[-1]["id"], 14)
        os.remove("test.db")

    def test_get(self):

        store = SQLiteDataStore(
            {"name": "test.db", "table": "address"}, ApiModel)

        for i in range(100):
            store.create({"name": "bob", "age": 34})

        self.assertEqual(store.get(10)["id"], 10)
        self.assertRaises(NotFound,
                          store.get,
                          101)
        os.remove("test.db")

    def test_create(self):
        data = {"name": "test.db", "table": "address"}
        store = SQLiteDataStore(
            data,
            ApiModel)

        self.assertRaises(NotFound,
                          store.get,
                          1)
        self.assertEqual(store.create({"name": "bob", "age": 34}), 1)
        self.assertEqual(store.create({"name": "bob", "age": 35}), 2)
        self.assertEqual(store.create({"name": "bob", "age": 34}), 3)
        print store.get(3)
        self.assertEqual(store.get(3)["id"], 3)
        os.remove("test.db")

    def test_update(self):
        store = SQLiteDataStore(
            {"name": "test.db", "table": "address"},
            ApiModel)

        for i in range(100):
            store.create({"name": "bob", "age": 34})

        self.assertEqual(
            store.update(
                {"name": "bob", "age": 34, "id": 34},
                {"name": "boby mc gee"}
                ),{"name": "boby mc gee", "age": 34, "id": 34})
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
        os.remove("test.db")

    def test_delete(self):
        store = SQLiteDataStore(
            {"name": "test.db", "table": "address"}, ApiModel)

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
        os.remove("test.db")


# class ApiStoreTest(TestCase):

#     def test_validation(self):
#         store = ApiDataStore(
#             "https://www.googleapis.com/youtube/v3/videos",
#             ApiModel,
#             list_key="items",
#             paginate_by=10,
#             limit="maxResults")
#         self.assertEqual(
#             len(store.get_list(key="AIzaSyChqwezk7uWrdXfhx27Bdz_1dF_ZWukPZM",
#                                part="snippet",
#                                mine="true",
#                                order="rating",
#                                type="video",
#                                chart="mostPopular"
#                                )), 10)

#     def test_get(self):
#         store = ApiDataStore(
#             "https://www.googleapis.com/youtube/v3/videos",
#             ApiModel,
#             list_key="items",
#             paginate_by=10,
#             limit="maxResults",
#             chart="mostPopular")


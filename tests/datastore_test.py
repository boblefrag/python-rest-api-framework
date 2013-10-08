from unittest import TestCase
from rest_api_framework.datastore import (PythonListDataStore,
                                          SQLDataStore)
from werkzeug.exceptions import BadRequest, NotFound


options = {
    "description": {
        "name": {
            "type": basestring, "required": True},
        "age": {
            "type": int, "required": True},
        "id": {
            "type": "autoincrement", "required": False}
        }
    }


class PythonListDataStoreTest(TestCase):

    def test_validation(self):

        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list, **options)
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

        store = PythonListDataStore(data_list, paginate_by=10, **options)
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
        store = PythonListDataStore(data_list, **options)
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

        store = PythonListDataStore(data_list, **options)
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

        store = PythonListDataStore(data_list, **options)
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

        store = PythonListDataStore(data_list, **options)
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

        store = PythonListDataStore(data_list, **options)
        self.assertEqual(len(store.filter(age=24)), 1)
        self.assertEqual(len(store.filter(name="bob")), 100)
        self.assertEqual(len(store.filter(name="john")), 0)
        self.assertEqual(len(store.filter(name="bob", age=12)), 1)


class SQLDataStoreTest(TestCase):

    def test_validation(self):
        store = SQLDataStore(
            {"name": "test_db", "table": "address"},
            **options)
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
        store = SQLDataStore(
            {"name": "test.db", "table": "address"},
            paginate_by=10,
            **options)
        for i in range(100):
            store.create({"name": "bob", "age": 34})
        self.assertEqual(len(store.get_list()), 10)
        self.assertEqual(store.get_list(start=10)[0]["id"], 10)
        self.assertEqual(store.get_list(end=15)[-1]["id"], 14)

    def test_get(self):

        store = SQLDataStore(
            {"name": "test.db", "table": "address"},
            **options)

        for i in range(100):
            store.create({"name": "bob", "age": 34})

        self.assertEqual(store.get(10)["id"], 10)
        self.assertRaises(NotFound,
                          store.get,
                          101)

    def test_create(self):

        store = SQLDataStore(
            {"name": "test.db", "table": "address"},
            **options)

        self.assertRaises(NotFound,
                          store.get,
                          1)
        self.assertEqual(store.create({"name": "bob", "age": 34}), 1)
        self.assertEqual(store.create({"name": "bob", "age": 35}), 2)
        self.assertEqual(store.create({"name": "bob", "age": 34}), 3)
        print store.get(3)
        self.assertEqual(store.get(3)["id"], 3)

    def test_update(self):
        store = SQLDataStore(
            {"name": "test.db", "table": "address"},
            **options)

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

    def test_delete(self):
        store = SQLDataStore(
            {"name": "test.db", "table": "address"},
            **options)

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

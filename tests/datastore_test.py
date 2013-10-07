from unittest import TestCase
from rest_api_framework.datastore import PythonListDataStore, DataStore
from werkzeug.exceptions import BadRequest, NotFound


class PythonListDataStoreTest(TestCase):

    def test_validation(self):

        data_list = [
            {"name": "bob",
             "age": a,
             "id": a
             } for a in range(100)
            ]

        store = PythonListDataStore(data_list)
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

        store = PythonListDataStore(data_list, paginate_by=10)
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
        store = PythonListDataStore(data_list)
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

        store = PythonListDataStore(data_list)
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

        store = PythonListDataStore(data_list)
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

        store = PythonListDataStore(data_list)
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

        store = PythonListDataStore(data_list)
        self.assertEqual(len(store.filter(age=24)), 1)
        self.assertEqual(len(store.filter(name="bob")), 100)
        self.assertEqual(len(store.filter(name="john")), 0)
        self.assertEqual(len(store.filter(name="bob", age=12)), 1)
        self.assertRaises(BadRequest,
                          store.filter,
                          **{"test": "something"}
                          )

Working with Pagination
=======================

Creating fixtures
-----------------

When your address book will be full of entry, you will need to add a
pagination on your API. As it is a common need, REST API Framework
implement a very easy way of doing so.

Before you can play with the pagination process, you will need to
create more data. You can create those records the way you want:

* direct insert into the database

.. code-block:: bash

    sqlite3 adress_book.db
    INSERT INTO users VALUES ("Nick", "Furry", 6);

* using the datastore directly

.. code-block:: python

    store = SQLiteDataStore({"name": "adress_book.db", "table": "users"}, UserModel)
    store.create({"first_name": "Nick", "last_name": "Furry"})

* using your API

.. code-block:: python

    curl -i -H "Content-type: application/json" -X POST -d '{"first_name": "Nick", "last_name": "Furry"}'  http://localhost:5000/users/

each on of those methods have advantages and disavantages but they all
make the work done. For this example, I propose to use the well know
requests package with a script to create a bunch of random records:

For this to work you need to install resquests : http://docs.python-requests.org/en/latest/user/install/#install

.. code-block:: python

    import json
    import requests
    import random
    import string

    def get_random():
        return ''.join(
                       random.choice(
                         string.ascii_letters) for x in range(
                         int(random.random() * 20)
                         )
                       )

    for i in range(200):
        requests.post("http://localhost:5000/users/", data=json.dumps({"first_name": get_random(), "last_name": get_random()}))

Pagination
----------

Now your datastore is filled with more than 200 records, it's time to
paginate. To do so import Pagination and change the controller part of
your app.

.. code-block:: python

    from rest_api_framework.pagination import Pagination

    class UserEndPoint(Controller):
        ressource = {
            "ressource_name": "users",
            "ressource": {"name": "adress_book.db", "table": "users"},
            "model": UserModel,
            "datastore": SQLiteDataStore,
            "options": {"validators": [UniqueTogether("first_name", "last_name")]}
            }

        controller = {
            "list_verbs": ["GET", "POST"],
            "unique_verbs": ["GET", "PUT", "DElETE"],
            "options": {"pagination": Pagination(20)}
            }

        view = {"response_class": JsonResponse,
                "options": {"formaters": ["add_ressource_uri", remove_id]}}

and try your new pagination:

.. code-block:: bash

    curl -i "http://localhost:5000/users/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 1811
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 11:32:55 GMT

    {
    "meta": {
        "count": 20, 
        "filters": {}, 
        "next": "?offset=20", 
        "offset": 0, 
        "previous": "null", 
        "total_count": 802
    }, 
    "object_list": [
        {
            "first_name": "Captain", 
            "last_name": "America", 
            "ressource_uri": "/users/1/"
        }, 
        {
            "first_name": "Captain", 
            "last_name": "America", 
            "ressource_uri": "/users/3/"
        }, 
        {
            "first_name": "John", 
            "last_name": "Doe", 
            "ressource_uri": "/users/4/"
        }, 
        {
            "first_name": "arRFOSYZT", 
            "last_name": "", 
            "ressource_uri": "/users/5/"
        }, 
        {
            "first_name": "iUJsYORMuYeMUDy", 
            "last_name": "TqFpmcBQD", 
            "ressource_uri": "/users/6/"
        }, 
        {
            "first_name": "EU", 
            "last_name": "FMSAbcUJBSBDPaF", 
            "ressource_uri": "/users/7/"
        }, 
        {
            "first_name": "mWAwamrMQARXW", 
            "last_name": "yMNpEnYOPzY", 
            "ressource_uri": "/users/8/"
        }, 
        {
            "first_name": "y", 
            "last_name": "yNiKP", 
            "ressource_uri": "/users/9/"
        }, 
        {
            "first_name": "s", 
            "last_name": "TRT", 
            "ressource_uri": "/users/10/"
        }, 
        {
            "first_name": "", 
            "last_name": "zFUaBd", 
            "ressource_uri": "/users/11/"
        }, 
        {
            "first_name": "WA", 
            "last_name": "priJ", 
            "ressource_uri": "/users/12/"
        }, 
        {
            "first_name": "XvpLttDqFmR", 
            "last_name": "liU", 
            "ressource_uri": "/users/13/"
        }, 
        {
            "first_name": "ZhJqTgYoEUzmcN", 
            "last_name": "KKDqHJwJMxPSaTX", 
            "ressource_uri": "/users/14/"
        }, 
        {
            "first_name": "qvUxiKIATdKdkC", 
            "last_name": "wIVzfDlKCkjkHIaC", 
            "ressource_uri": "/users/15/"
        }, 
        {
            "first_name": "YSSMHxdDQQsW", 
            "last_name": "UaKCKgKsgEe", 
            "ressource_uri": "/users/16/"
        }, 
        {
            "first_name": "EKLFTPJLKDINZio", 
            "last_name": "nuilPTzHqattX", 
            "ressource_uri": "/users/17/"
        }, 
        {
            "first_name": "SPcDBtmDIi", 
            "last_name": "MrytYqElXiIxA", 
            "ressource_uri": "/users/18/"
        }, 
        {
            "first_name": "OHxNppXiYp", 
            "last_name": "AUvUXFRPICsJIB", 
            "ressource_uri": "/users/19/"
        }, 
        {
            "first_name": "WBFGxnoe", 
            "last_name": "KG", 
            "ressource_uri": "/users/20/"
        }, 
        {
            "first_name": "i", 
            "last_name": "ggLOcKPpMfgvVGtv", 
            "ressource_uri": "/users/21/"
        }
    ]
    }

Browsering Through Paginated objects
------------------------------------

Of course you get 20 records but the most usefull part is the meta
key:

.. code-block:: json

    {"meta":
        {"count": 20,
        "total_count": 802,
        "next": "?offset=20",
        "filters": {},
        "offset": 0,
        "previous": "null"}
    }

You can use the "next" key to retreive the 20 next rows:

.. code-block:: bash

    curl -i "http://localhost:5000/users/?offset=20"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 1849
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 11:38:59 GMT

.. code-block:: json

    {"meta": {"count": 20, "total_count": 802, "next": "?offset=40",
    "filters": {}, "offset": 20, "previous": "?offset=0"}, "object_list":
    [<snip for readability>]}

.. note::

   The count and offset keywords can be easily changed to match your
   needs. pagination class may take an offset_key and count_key
   parameters. So if you prefer to use first_id and limit, you can
   change your Paginator class to do so:

   .. code-block:: python

       "options": {"pagination": Pagination(20,
                                        offset_key="first_id",
                                        count_key="limit")

   Wich will results in the following:

   .. code-block:: bash

         curl -i "http://localhost:5000/users/"
         {"meta": {"first_id": 0, "total_count": 802, "next": "?first_id=20",
         "limit": 20, "filters": {}, "previous": "null"}, "object_list": [<snip
         for readability>]


Pagination and Filters
----------------------

Pagination and filtering play nice together

.. code-block:: bash

    curl -i "http://localhost:5000/users/?last_name=America"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 298
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 12:14:59 GMT

    {"meta": {"count": 20,
              "total_count": 2,
              "next": "null",
              "filters": {"last_name": "America"},
              "offset": 0,
              "previous": "null"},
              "object_list": [
                  {"first_name": "Joe",
                   "last_name": "America",
                   "ressource_uri": "/users/1/"},
                  {"first_name": "Bob",
                   "last_name": "America",
                   "ressource_uri": "/users/3/"}
              ]
     }

Next: :doc:`adding_endpoint`

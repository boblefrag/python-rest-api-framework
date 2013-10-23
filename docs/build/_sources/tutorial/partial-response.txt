Implementing Partial Response
=============================

You can give your user the ability to retreive only the data they need
instead of all of an object representation. For the adress field, some
can want to retreive only the country and the city field but do not
care about the others.

with Python REST API Framework, it's easy to make this happend.

First import the Partial base class:

.. code-block:: python

    from rest_api_framework.partials import Partial

Then add the partial option to the AddressEndPoint:

.. code-block:: python

    class AddressEndPoint(UserEndPoint):
        ressource = {
            "ressource_name": "address",
            "ressource": {"name": "adress_book.db", "table": "address"},
            "model": AddressModel,
            "datastore": SQLiteDataStore,
            "options": {"partial": Partial()}
            }

Test the Partial
----------------

.. code-block:: bash

    curl -i -X GET "http://localhost:5000/address/?accesskey=hackme&fields=city,country"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 241
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 15:50:27 GMT

    {
        "meta": {
            "count": 20, 
            "filters": {
                "accesskey": "hackme", 
                "fields": "city,country"
            }, 
            "next": "null", 
            "offset": 0, 
            "previous": "null", 
            "total_count": 1
        }, 
        "object_list": [
            {
                "city": "Paris", 
                "country": "France", 
                "ressource_uri": "/address/1/"
            }
        ]
    }

next: :doc:`whole_application`

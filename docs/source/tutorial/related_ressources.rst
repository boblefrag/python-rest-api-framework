Linking ressource together
==========================

Now that you have users and address, you want to link them
together. Adding a reference from a user to his user.

Not all the datastore can handle this type of relation but hopefully,
the SQLiteDataStore does.

First you will need to change your UserModel definition:

.. code-block:: python

    fields = [models.StringField(name="country", required=True),
              models.StringField(name="city", required=True),
              models.StringField(name="street", required=True),
              models.IntegerField(name="number", required=True),
              models.IntForeign(name="user",
                                foreign={"table": "users",
                                         "column": "id",
                                         }
                                ),
              models.PkField(name="id", required=True)
              ]

The part we added is:

.. code-block:: python

    models.IntForeign(name="address",
                      foreign={"table": "address",
                               "column": "id",
                               }
                      ),

This will add a foreign key constrain on the user ensuring the address
id you give corresspond to an existing address.

* table : is the table of the ressource your are linking
* column: is the column you will check for the constrain

.. note::

   unfortunately, at the time of writing, there is no way to
   update the schema automaticaly. You will need either to destroy
   your database (Python Rest Framework will create a fresh one) or do
   an alter table by hands. As this is just a tutorial, we will choose
   the second option and delete the file "adress.db"

   It's also important to note the your endpoints must be listed in
   the Wrapper in the order of foreing keys. First the model to link
   to, then the model that will be linked

Adding an adress
----------------

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d
    '{"country":"France", "city": "Paris", "street": "quais de Valmy",
    "number": 45}' http://localhost:5000/address/

    HTTP/1.0 201 CREATED
    Location: http://localhost:5000/address/1/
    Content-Type: application/json
    Content-Length: 0
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 17:23:49 GMT

Create a user linked to an address
----------------------------------

Because, as the API developper you know that
http://localhost:5000/address/1/ corresond to the address with the
"id" 1 you can create a user:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d
    '{"first_name":"Super", "last_name": "Dupont", "address": 1}'
    http://localhost:5000/users/

    HTTP/1.0 201 CREATED
    Location: http://localhost:5000/users/1/
    Content-Type: application/json
    Content-Length: 0
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 17:27:34 GMT

You can check that your Foreign constrain is working with:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d
    '{"first_name":"Super", "last_name": "Man", "address": 2}'
    http://localhost:5000/users/

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 38
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 17:30:03 GMT

    {"error": "address does not validate"}

This fail because address 2 does not exists.

Retreive the adress of a user
-----------------------------

If you now the user, it's easy to get the adress.

First get the user:

.. code-block:: bash

    curl -i http://localhost:5000/users/1/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 90
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 17:42:18 GMT

    {
    "address": 1, 
    "first_name": "Super", 
    "last_name": "Dupont", 
    "ressource_uri": "/users/1/"
    }

His adress has the id "1". We can issue a request:

.. code-block:: bash

    curl -i http://localhost:5000/address/1/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 112
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 17:44:07 GMT

    {
        "city": "Paris", 
        "country": "France", 
        "number": 45, 
        "ressource_uri": "/address/1/", 
        "street": "quais de Valmy"
    }

Retreive users from an adress
------------------------------

The same apply in the other side. As we know the adress id:

.. code-block:: bash

    curl -i http://localhost:5000/users/?address=1
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 228
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 17:46:13 GMT

    {
        "meta": {
            "count": 20, 
            "filters": {
                "address": "1"
            }, 
            "next": "null", 
            "offset": 0, 
            "previous": "null", 
            "total_count": 1
        }, 
        "object_list": [
            {
                "address": 1, 
                "first_name": "Super", 
                "last_name": "Dupont", 
                "ressource_uri": "/users/1/"
            }
        ]
    }

next: :doc:`represent_related`

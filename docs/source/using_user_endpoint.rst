Playing with the newly created endpoint
=======================================

First you can check that your endpoint is up

.. code-block:: bash

    curl -i "http://localhost:5000/users/"

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 44
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 11:13:44 GMT

    {
    "meta": {
        "filters": {}
    }, 
    "object_list": []
    }


Your endpoint is responding but does not have any data. Let's add
some:

Create a user
-------------

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d '{"first_name":"John", "last_name": "Doe"}'  http://localhost:5000/users/

    HTTP/1.0 201 CREATED
    Location: http://localhost:5000/users/1/
    Content-Type: application/json
    Content-Length: 0
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 13:00:13 GMT

If you look carfully at the response, you can see the header
"Location" giving you the ressource uri of the ressource you just
created. This is usefull if you want to retreive your object. Let's
get a try:

List and Get
------------

.. code-block:: bash

    curl -i "http://localhost:5000/users/1/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 51
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 16:53:19 GMT

    {
    "first_name": "John", 
    "id": 1, 
    "last_name": "Doe", 
    "ressource_uri": "/users/1/"
    }


You can see that ressource_uri was not part of the ressource. It have
been added by the View itself. View can add multiple
metadata, remove or change some fields and so on. More on that in
:doc:`representing_data`


The list of users is also updated:

.. code-block:: bash

    curl -i "http://localhost:5000/users/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 83
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 17:03:00 GMT

    {
    "meta": {
        "filters": {}
    }, 
    "object_list": [
        {
            "first_name": "John", 
            "id": 1, 
            "last_name": "Doe", 
            "ressource_uri": "/users/1/"
        }
    ]
    }


Delete a user
-------------
Let's add a new user:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d '{"first_name":"Peter", "last_name": "Something"}'  http://localhost:5000/users/

    HTTP/1.0 201 CREATED
    Location: http://localhost:5000/users/2/
    Content-Type: application/json
    Content-Length: 0
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 13:00:13 GMT

and now delete it:

.. code-block:: bash

    curl -i -X DELETE "http://localhost:5000/users/2/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 0
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 20:41:46 GMT

You can check that the user no longer exists:

.. code-block:: bash

    curl -i "http://localhost:5000/users/2/"
    HTTP/1.0 404 NOT FOUND
    Content-Type: application/json
    Connection: close
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 11:16:33 GMT

    { "error": "<p>The requested URL was not found on the
    server.</p><p>If you entered the URL manually please check your
    spelling and try again.</p>" }


And the list is also updated:

.. code-block:: bash

    curl -i "http://localhost:5000/users/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 125
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 11:17:46 GMT

    {
    "meta": {
        "filters": {}
    }, 
    "object_list": [
        {
            "first_name": "John", 
            "id": 1, 
            "last_name": "Doe", 
            "ressource_uri": "/users/1/"
        }
    ]
    }


Update a User
-------------

Let's go another time to the creation process:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d '{"first_name":"Steve", "last_name": "Roger"}'  http://localhost:5000/users/
    HTTP/1.0 201 CREATED
    Location: http://localhost:5000/users/3/
    Content-Type: application/json
    Content-Length: 0
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 20:45:38 GMT

But well everybody now that Steve Roger real name is Captain
America. Let's update this user:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X PUT -d '{"first_name":"Capitain", "last_name": "America"}'  http://localhost:5000/users/3/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 58
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 20:57:47 GMT

    {"first_name": "Capitain", "last_name": "America", "id": 3, "ressource_uri": "/users/3/"}

Argh! Thats a typo. the fist name is "Captain", not "Capitain". Let's
correct this:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X PUT -d '{"first_name":"Captain"}'  http://localhost:5000/users/3/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 59
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 21:08:04 GMT

    {"first_name": "Captain", "last_name": "America", "id": 3, "ressource_uri": "/users/3/"}


Filtering
---------

Ressources can be filtered easily using parameters:

.. code-block:: bash

    curl -i "http://localhost:5000/users/?last_name=America"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 236
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 12:07:21 GMT

    {"meta": {"filters": {"last_name": "America"}}, "object_list":
    [{"first_name": "Joe", "last_name": "America", "id": 1,
    "ressource_uri": "/users/1/"}, {"first_name": "Bob", "last_name":
    "America", "id": 3, "ressource_uri": "/users/3/"}]

Multiple filters are allowed:

.. code-block:: bash

    curl -i "http://localhost:5000/users/?last_name=America&first_name=Joe"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 171
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 12:09:32 GMT

    {"meta": {"filters": {"first_name": "Joe", "last_name": "America"}},
    "object_list": [{"first_name": "Joe", "last_name": "America", "id": 1,
    "ressource_uri": "/users/1/"}]}

Error handling
--------------

Of course, If data is not formated as expected by the API, the base
error handling take place.


Missing data
~~~~~~~~~~~~

If you don't provide a last_name, the API will raise a BAD REQUEST
explaining your error:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d '{"first_name":"John"}'  http://localhost:5000/users/

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 62
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 13:21:10 GMT

    {"error": "last_name is missing. Cannot create the ressource"}

Invalid Data
~~~~~~~~~~~~

The same apply if you dont give coherent data:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d '{"first_name":45, "last_name": "Doe"}'  http://localhost:5000/users/

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 41
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 13:24:53 GMT
    {"error": "first_name does not validate"}

however, there is no duplicate check. So you can create as many "John
Doe" you want. This could be a huge problem if your not able to
validate uniqueness of a user. For the API, this is not a problem
because each user is uniquely identified by his id.

If you need to ensure it can be only one John Doe, you must add a
validator on your datastore.


Autodocumentation
-----------------

Your API is autodocumented by Python REST API Framework.

.. code-block:: bash

    curl -i -X GET http://localhost:5000/schema/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 268
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 08:24:13 GMT


    {
        "users": {
            "allowed list_verbs": [
                "GET", 
                "POST"
            ], 
            "allowed unique ressource": [
                "GET", 
                "PUT", 
                "DElETE"
            ], 
            "list_endpoint": "/users/", 
            "schema_endpoint": "/schema/users/"
        }
    }

.. code-block:: bash

    url -i -X GET http://localhost:5000/schema/users/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 206
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 09:04:16 GMT

    {
        "first_name": {
            "example": "Hello World", 
            "required": "true", 
            "type": "string"
        }, 
        "last_name": {
            "example": "Hello World", 
            "required": "true", 
            "type": "string"
        }
    }



Next: :doc:`adding_validator_datastore`


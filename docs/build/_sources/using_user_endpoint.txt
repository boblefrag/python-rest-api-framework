Playing with the newly created endpoint
=======================================

First you can check that your endpoint is up

.. code-block:: bash

    curl -i "http://localhost:5000/users/"

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 2
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 12:52:22 GMT

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

    {"first_name": "John", "last_name": "Doe", "id": 1, "ressource_uri": "/users/1/"}

You can see that ressource_uri was not part of the ressource. It have
been added by the View itself. View can add multiple
metadata, remove or change some fields and so on. More on that in
:doc:`representing_data`


The list of users is also updated:

.. code-block:: bash

    curl -i "http://localhost:5000/users/1/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 83
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 17:03:00 GMT

    [{"first_name": "John", "last_name": "Doe", "id": 1, "ressource_uri": "/users/1/"}]

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

Update a User
=============

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

    curl -i -H "Content-type: application/json" -X PUT -d '{"first_name":"Captain", "last_name": "America"}'  http://localhost:5000/users/3/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 58
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 20:57:47 GMT

Partial update is also possible:

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X PUT -d '{"first_name":"Cap tain"}'  http://localhost:5000/users/3/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 59
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 21:08:04 GMT


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

Next: :doc:`adding_validator_datastore`

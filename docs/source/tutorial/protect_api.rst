Authentication and Authorization: Protecting your API
=====================================================

Authentication and Authorization are different topics as you can
implement Authentication without Authorization (For rate-limiting or
loggin for example).

Authentication
--------------

The fist thing you can do is to add an Authentication
backend. Authentication backend needs a datastore to retreive the user
accessing the API. This datastore can be used by another endpoint of
your API or a datastore aimed for this purpose only.

In this example, we will use a very simple datastore, meant for
testing purpose: the PythonListDataStore.

Define a backend
----------------

The PythonListDataStore is just a list of python dictionnary. So let's
first create this list:

.. code-block:: python

    ressources = [{"accesskey": "hackme"}, {"accesskey": "nopassword"}]

Like any other datastore, you need a Model to describe your datastore:

.. code-block:: python

    class KeyModel(models.Model):
        fields = [
            models.StringPkField(name="accesskey", required=True)
            ]

Then you can instanciate your datastore:

.. code-block:: python

    from rest_api_framework.datastore import PythonListDataStore

    datastore = PythonListDataStore(ressources, KeyModel)

Instanciate the Authentication backend
--------------------------------------

To keep this example simple we will use another testing tool, the
ApiKeyAuthentication

ApiKeyAuthentication will inspect the query for an "apikey"
parameter. If the "apikey" correspond to an existing object in the
datastore, it will return this object. Otherwise, the user is
anonymous.

.. code-block:: python

    from rest_api_framework.authentication import ApiKeyAuthentication
    authentication = ApiKeyAuthentication(datastore, identifier="accesskey")

Then you can plug this authentication backend to your endpoint:

.. code-block:: python

    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DElETE"],
        "options": {"pagination": Pagination(20),
                    "formaters": [foreign_keys_format],
                    "authentication": authentication}
        }

Instanciate the Authorization backend
-------------------------------------

The Authorization backend relies on the Authentication backend to
retreive a user. With this user and the request, it will grant access
or raise an Unauthorized error.

For this example we will use the base Authentication class. This class
tries to authenticate the user. If the user is authenticated, then
access is granted. Otherwise, it is not.

from rest_api_framework.authentication import Authorization
 then add it to the controller options:

.. code-block:: python

    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DElETE"],
        "options": {"pagination": Pagination(20),
                    "formaters": [foreign_keys_format],
                    "authentication": authentication,
                    "authorization": Authorization,
                    }
        }

Testing Authentication and Authorization Backend
------------------------------------------------

Let's give a try:

.. code-block:: python

    curl -i -X GET http://localhost:5000/users/?accesskey=hackme
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 350
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 12:18:52 GMT


    curl -i -X GET http://localhost:5000/users/?accesskey=helloworld
    HTTP/1.0 401 UNAUTHORIZED
    Content-Type: application/json
    Content-Length: 350
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 12:19:26 GMT

    curl -i -X GET http://localhost:5000/users/
    HTTP/1.0 401 UNAUTHORIZED
    Content-Type: application/json
    Content-Length: 350
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 12:19:45 GMT

next: :doc:`rate-limit`

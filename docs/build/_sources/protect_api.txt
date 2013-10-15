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

    ressource = [{"accesskey": "hackme", "accesskey": "nopassword"}]

Like any other datastore, you need a Model to describe your datastore:

.. code-block:: python

    class KeyModel(models.Model):
        fields = [
            models.StringPkField(name="id", required=True)
            ]

Then you can instanciate your datastore:

from rest_api_framework.datastore import PythonListDataStore

.. code-block:: python

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
    authentication = ApiKeyAuthentication(datastore)

Then you can plug this authentication backend to your endpoint:

.. code-block:: python

    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DElETE"],
        "options": {"pagination": Pagination(20),
                    "formaters": [foreign_keys_format],
                    "authentication": authentication,}
        }

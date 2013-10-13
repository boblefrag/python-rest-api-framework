Authentication and Authorization
================================

Endpoint can be easily protected with a custom or existing
backend. Authentication and Authorization are given as argument to the
Controller. Authorization backend will be given the request
object. You can then have a very fine grained control on
Authorization.

Authentication
--------------

Authentication implement the get_user(identifier) method. As
Authentication need to read the list of users somewhere, it need a
datastore to work with.

As always, datastore can be anything from a simple python list, a
database, another api and so on.

Authentication return the user object the datastore provide

Example
~~~~~~~

.. code-block:: python

    class ApiKeyAuthentication(Authentication):

        def __init__(self, datastore, **options):
            self.datastore = datastore

        def get_user(self, identifier):
            try:
                user = self.datastore.get(identifier)
                return user
            except NotFound:
                return None

Authorization
-------------

Authorization need a way to indentify a user. An Authentication
backend is used for this need.

They implements the check_auth(request) method. This method should
return None if authorization is granted or raise an Unauthorized error
otherwise.

.. note::

   this documentation use "user" as a placeholder. You do not need a
   user. Only something to identify the request. This could be
   anything from a hash, a password, public key and so on...

Example
~~~~~~~

.. code-block:: python

    class ApiKeyAuthorization(Authorization):
        """
        This authentication backend use an api key to authenticate and
        authorize users
        """
        def __init__(self, authentication, **options):
            self.authentication = authentication

        def check_auth(self, request):
            """
            Check if a user is authorized to perform a particular action.
            """
            data = request.values.to_dict()
            if "apikey" in data:
                if self.authentication.get_user(data['apikey']):
                    return
                else:
                    raise Unauthorized

            raise Unauthorized

How to use an Authentication/Authorization backend
---------------------------------------------------

For this example we will use a very simple datastore ressource for
authentication purpose :

.. code-block:: python

    ressources = [{"id": "azerty"}]

The ressource is a python dict. Is ok to use the PythonListDataStore
to connect to the ressource.

The model will be simple too:


.. code-block:: python

    class AuthModel(models.Model):
        fields = [
            models.StringField(name="id", required=True)
            ]

Then here is our datastore fully functional:

.. code-block:: python

    datastore = PythonListDataStore(ressources, AuthModel)

Then we can instanciate an ApiKeyAuthentication :

.. code-block:: python

    authentication = ApiKeyAuthentication(datastore)

Finnaly, ApiKeyAuthorization can be instanciated too:

.. code-block:: python

    auth = ApiKeyAuthorization

You can now use any of your api and protect it with the
ApiKeyAuthorization you just created:

.. code-block:: python

       class ApiAppAuth(Controller):
            controller = {
                "options": {"authentication": auth,
                            "authorization": ApiKeyAuthorization
                            }
                }
            <other arguments>...

Each time a user access this api, he must use ?apikey=azerty to be
granted access to the api.

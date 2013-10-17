Adding validators to your DataStore
===================================

In this exemple, you want to check that a user with the same last_name
and same first_name does not exist in your datastore before creating a
new user.

For this you can use UniqueTogether:

UniqueTogether
--------------

Change your UserEndPoint to get:

.. code-block:: python

    from rest_api_framework.datastore.validators import UniqueTogether

    class UserEndPoint(Controller):
        ressource = {
            "ressource_name": "users",
            "ressource": {"name": "adress_book.db", "table": "users"},
            "model": UserModel,
            "datastore": SQLiteDataStore,
            "options":{"validators": [UniqueTogether("first_name", "last_name")]}
            }

        controller = {
            "list_verbs": ["GET", "POST"],
            "unique_verbs": ["GET", "PUT", "DElETE"]
            }

        view = {"response_class": JsonResponse}

each of ressource, controller and views can have various options to
add new functionality to them. The "validators" option of ressource
enable some datastore based validators. As you can see, validators are
a list. This meen that you can add many validators for a single datastore.

UniqueTogether will ensure that a user with first_name: John and
last_name: Doe cannot be created.

Let's try:

.. code-block:: python

    curl -i -H "Content-type: application/json" -X POST -d '{"first_name": "John", "last_name": "Doe"}'  http://localhost:5000/users/
    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 57
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 17:13:41 GMT

    {"error": "first_name,last_name must be unique together"}

Next: :doc:`representing_data`

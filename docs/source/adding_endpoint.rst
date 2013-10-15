Loading multiple endpoint
=========================

Now that your fist endpoint work as expected, you will need to add an
address field on the user model. But as some users can have the same
address, and because you want to retreive some user using an address,
you will need to create an new endpoint:

Define a new model
------------------


.. code-block:: python

    class AddressModel(models.Model):

        fields = [models.StringField(name="country", required=True),
                  models.StringField(name="city", required=True),
                  models.StringField(name="street", required=True),
                  models.IntegerField(name="number", required=True),
                  models.PkField(name="id", required=True)
                  ]

Inherite from previous apps
---------------------------

The only thing that change here in comparisson to the UserEndPoint you
created earlier is the ressource dict. So instead of copy pasting a
lot of lines, let's heritate from your first app:

.. code-block:: python

    class AddressEndPoint(UserEndPoint):
        ressource = {
            "ressource_name": "address",
            "ressource": {"name": "adress_book.db", "table": "address"},
            "model": AddressModel,
            "datastore": SQLiteDataStore
            }

All the options already defined in the UserEndPoint will be available
with this new one. Pagination, formater and so on.

Of course, if you change the controller or the view of UserEndPoint,
AddressEndPoint will change too. If it become a problem, you'll have
to create a base class with common options and configurations and each
of your endpoints will inherit from this base class. Each endpoint
will be able to change some specifics settings.

The last thing to do to enable your new endpoint is to add it to the
WSGIDispatcher

Add the app to the dispatcher
-----------------------------

.. code-block:: python

    if __name__ == '__main__':
        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([AddressEndPoint, UserEndPoint])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

.. note::

   For now the order you register AddressEndPoint and UserEndPoint
   doesn't make a difference. But we will add a reference from the
   user table to the address table. At this point, you will need to
   reference AddressEndPoint before UserEndPoint.


Check that everything work
--------------------------

.. code-block:: python

    curl -i "http://localhost:5000/address/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 124
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 15:45:34 GMT

    {
    "meta": {
        "count": 20,
        "filters": {},
        "next": "null",
        "offset": 0,
        "previous": "null",
        "total_count": 0
    },
    "object_list": []
    }

next: :doc:`related_ressources`

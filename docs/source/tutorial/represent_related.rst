Representing relations
======================

Even if now can query adress from a user and users from an adress,
your users cannot know that the field "address": 1 correspond to
/address/1/ plus it break a common rule. The id of the relation
correspond to yor internal logic. Users doesn't have to know how it
work, they just have to use it.

What we will try to do in this part of the tutorial is the following:

* http://localhost:5000/users/1/ should return:

.. code-block:: json

    {
        "address": /address/1/,
        "first_name": "Super",
        "last_name": "Dupont",
        "ressource_uri": "/users/1/"
    }

* this request should work

.. code-block:: bash

  curl -i -H "Content-type: application/json" -X POST -d
  '{"first_name":"Super", "last_name": "Dupont", "address":
  "/adress/1/"}'  http://localhost:5000/users/

* Of course, http://localhost:5000/users/?address=/adress/1/" should
  return the users with this address.

Representiing the relation on the user side
-------------------------------------------

This is the simplest task because you already changed the response
result by adding remove_id function to the list of View formater in
:doc:`representing_data`

.. code-block:: python

    def format_address(response, obj):
        obj['address'] = "/address/{0}".format(obj['address'])
        return obj


Sure this method will work but if you get a close look on how
ForeignKeyField (IntForeign inherit from this class) You will see that
the ForeignKeyField is filled with th options parameter you gave at
the foreign key creation. You can so write:

.. code-block:: python

    def format_foreign_key(response, obj):
        from rest_api_framework.models.fields import ForeignKeyField
        for f in response.model.get_fields():
            if isinstance(f, ForeignKeyField):
                obj[f.name] = "/{0}/{1}/".format(f.options["foreign"]["table"],
                                                 obj[f.name])
        return obj

This function can then be used in all your project when you need to
translate a foreignkey into a meaning full ressource uri

For now, you can add this function to the list of formaters in your
UserEndPoint views:

.. code-block:: python

    view = {"response_class": JsonResponse,
            "options": {"formaters": ["add_ressource_uri",
                                      remove_id,
                                      format_foreign_key

                                      ]}}

Check the formater
------------------

.. code-block:: python

    curl -i http://localhost:5000/users/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 226
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 21:21:44 GMT

    {
        "meta": {
            "count": 20,
            "filters": {},
            "next": "null",
            "offset": 0,
            "previous": "null",
            "total_count": 1
        },
        "object_list": [
            {
                "address": "/address/1/",
                "first_name": "Super",
                "last_name": "Dupont",
                "ressource_uri": "/users/1/"
            }
        ]
    }

Formating data for the system
-----------------------------

Because you hide the internal implementation of your API to your user,
you have to give him a way to interact with your API.

To do so, you need to create a formater, exactly like you have done
for the View. But this time you must do it for the Controller.

.. code-block:: python

    def foreign_keys_format(view, obj):
        from rest_api_framework.models.fields import ForeignKeyField
        for f in view.datastore.model.get_fields():
            if isinstance(f, ForeignKeyField):
                if obj.get(f.name):
                    obj[f.name] = int(obj[f.name].split("/")[-2])
        return obj

and add it to the controller formater. Change the UserEndPoint
controller:

.. code-block:: python

    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DElETE"],
        "options": {"pagination": Pagination(20),
                    "formaters": [foreign_keys_format]}
        }

Now, each time the endpoint will deal with a data fields corresponding
to a ForeignKeyField it will retreive the id from the url supplied

"/address/1/" will be translated in 1

Check the Controller translation
--------------------------------

.. code-block:: bash

    curl -i -H "Content-type: application/json" -X POST -d
    '{"first_name":"Captain", "last_name": "America", "address":
    "/adress/1/"}'  http://localhost:5000/users/


    HTTP/1.0 201 CREATED
    Location: http://localhost:5000/users/2/
    Content-Type: application/json
    Content-Length: 0
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 22:23:43 GMT

.. code-block:: bash

    curl -i http://localhost:5000/users/?address=/adress/1/
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 341
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Tue, 15 Oct 2013 22:33:47 GMT

    {
        "meta": {
            "count": 20, 
            "filters": {
                "address": 1
            }, 
            "next": "null", 
            "offset": 0, 
            "previous": "null", 
            "total_count": 2
        }, 
        "object_list": [
            {
                "address": "/address/1/", 
                "first_name": "Super", 
                "last_name": "Dupont", 
                "ressource_uri": "/users/1/"
            }, 
            {
                "address": "/address/1/", 
                "first_name": "Supe", 
                "last_name": "Dupont", 
                "ressource_uri": "/users/2/"
            }
        ]
    }

next: :doc:`protect_api`

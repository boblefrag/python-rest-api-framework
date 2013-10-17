Show data to users
==================

The view you have used so far just added a ressource_uri. But preserve
the id attribut. As id is an internal representation of the data you
may wich to remove it.

Define a formater function
--------------------------

To do so you'll have to write a simple function to plug on the
view. This function is a formater. When the View instanciate the
formater, it give you access to the response object and the object to
be rendered.

Because you want to remove the id of the reprensentaion of your
ressource, you can write:

.. code-block:: python

    def remove_id(response, obj):
        obj.pop("id")
        return obj

and change the view part of your UserEndPoint as follow:

.. code-block:: python

    view = {"response_class": JsonResponse,
            "options": {"formaters": ["add_ressource_uri",
            remove_id]}}

add_ressource_uri is the default formatter for this View. You dont
need to remove it for now. But if you try, then it will work as
expected. The ressource_uri field will be removed.

The idea behind Python REST API Framework is to always get out of
your way.

You can check that it work as expected:

.. code-block:: bash

    curl -i "http://localhost:5000/users/1/"
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 80
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Mon, 14 Oct 2013 23:41:55 GMT

    {"first_name": "Captain", "last_name": "America",
    "ressource_uri": "/users/1/"}

Make things generics
--------------------

This implementation work on your endpoint because you each object has
an id. But, if later you create another endpoint with ressources
lacking the "id" key, you'll have to re-write your function.

Instead, you can take advantage of the response wich is part of the
parameters of your function.

response object carry the attribut model who define your ressources
fields. You can then get the name of the Pk field used with this
ressource with:

.. code-block:: python

    response.model.pk_field.name

Your code then become:

.. code-block:: python

    def remove_id(response, obj):
        obj.pop(response.model.pk_field.name)
        return obj

And reuse this formatter as long as you need.

Formaters are here to help you build clean and meaningful ressources
representations. It should hide internal representation of your
ressources and return all of the fields needed to manipulate and
represent your data.

Next :doc:`work_with_pagination`

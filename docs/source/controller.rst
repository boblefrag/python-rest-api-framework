Controllers
===========

Controller manage the dialogue between the request and the
datastore. Controller handle all the request related stuff:

* Pagination
* Authentication
* Authorization
* Rate-Limit
* Authorized verbs


Mandatory Arguments
-------------------

When creating a controller, some arguments are mandatory. It define
how your controller should handle requests.

* list_verbs: list_verbs will tell your controller wich verbs are
  allowed at the root of your ressource. ["GET", "POST"] for a read
  and write API, and only ["GET"] for a read-only API

* unique_verbs: unique verbs tell your controller wich verbs are
  allowed at the unique identifier endpoint of your ressource
  (/ressource_name/<unique_id>). ["GET", "PUT", "DELETE"] fa read and
  write API, ["GET"] for a read-only API.

Optionals parameters
--------------------

Optionals parameters make your api able to manage special features
like Pagination, Authentication, Authorization and Rate-Limit. They
each depend on your own implementation.

Exemples:

.. code-block:: python

    controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DElETE"],
        "options": {"pagination": Pagination(20)}
        }

This will create:

* a read and write API (GET and POST on the root URL, GET, PUT and
  DELETE on the detail URL)

* with a pagination of 20 results max because of the optional
  pagination parameter. Results will be paginated using the offset and
  count keyword (see :doc:`pagination`) to get more on this topic.

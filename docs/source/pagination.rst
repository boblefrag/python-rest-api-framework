Paginate a ressource
====================

When you build your endpoint, each ressource can be
paginated. Pagination is enabled in the controller argument of an
application. See :doc:`controller` for more information about
controller configuration.

When you want to enable pagination on a ressource, you should use a
Pagination class. You can directly use :class:`.rest_api_framework.pagination.Pagination`
or create your own pagination mechanism inheriting from this class

Max, Offset and Count
---------------------

Pagination should define some attributs:

* max
* offset_key
* count_key

Those attributs are not mandatory, you can create a Pagination based
on a token for exemple. (see below). But here how the base pagination
mechanism work.

The base Pagination class enable the choice of those attributs when
instanciated. For example:

.. code-block:: python

   controller = {
        "list_verbs": ["GET", "POST"],
        "unique_verbs": ["GET", "PUT", "DElETE"],
        "options": {"pagination": Pagination(20,
                                             offset_key="start",
                                             count_key="limit")}
        }

Define like this, one should get the 20th to 30th results of the
ressource "dogs" like this:

.. code-block:: bash

   curl -i "http://<domain>.<ext>/dogs/?start=20&limit=10"


The paginate method
-------------------

A paginate method take the request as argument and should return :

* offset
* count
* request kwargs

As pagination take some kwargs from the request to calculate offset
and count, it is possible to remove those keyword arguments from the
orignal request arguments. In the above example, the filter method of
the datastore will only receive an empty dict to filter the dogs
ressources.

Other pagination implementations
--------------------------------

One should need to give a pagination based on a token instead of
offset and count. But as datastore will always paginate using start
and offset, the paginate method should be able to calculate those
values from the token. It's up to you to create this method. This
should not be a problem because you have the whole request to work on.


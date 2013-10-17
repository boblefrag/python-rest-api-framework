Rate Limiting your endpoints
============================

Now that your users are authenticated and that you put an
authorization backend, you can add a rate limit on your api. Rate
limit will prevent your users to over use your endpoints.

With rate limit, a user can call your API at a certain rate. A number
of calls per an interval. You have to decide how many call and wich
interval.

For this example, let say something like 100 call per 10 minutes. For
Python REST Framework, interval are counted in seconds so 10 minutes
equals 10*60 = 600

Create a datastore for rate-limit:
----------------------------------

The rate-limit implementation need a datastore to store
rate-limit. Let's create one:

.. code-block:: python

        class RateLimitModel(models.Model):
            fields = [models.StringPkField(name="access_key"),
                      models.IntegerField(name="quota"),
                      models.TimestampField(name="last_request")]


You can then add your new datastore to the list of options of you
controller:


Add Rate-limit to your API
--------------------------

.. code-block:: python

    from rest_api_framework.ratelimit import RateLimit

        controller = {
            "list_verbs": ["GET", "POST"],
            "unique_verbs": ["GET", "PUT", "DElETE"],
            "options": {"pagination": Pagination(20),
                        "formaters": [foreign_keys_format],
                        "authentication": authentication,
                        "authorization": Authorization,
                        "ratelimit": RateLimit(
                    PythonListDataStore([],RateLimitModel),
                    interval=10*60,
                    quota=100)
                        }
            }

Test!
-----

.. code-block:: bash

    curl -i -X GET http://localhost:5000/users/?accesskey=hackme
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 350
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 15:22:12 GMT

    {"meta": {"count": 20, "total_count": 2, "next": "null", "filters":
    {"accesskey": "hackme"}, "offset": 0, "previous": "null"},
    "object_list": [{"ressource_uri": "/users/1/", "first_name": "Super",
    "last_name": "Dupont", "address": "/address/1/"}, {"ressource_uri":
    "/users/2/", "first_name": "Supe", "last_name": "Dupont", "address":
    "/address/1/"}]}

.. code-block:: bash

    curl -i -X GET http://localhost:5000/users/?accesskey=hackme
    HTTP/1.0 429 TOO MANY REQUESTS
    Content-Type: application/json
    Content-Length: 23
    Server: Werkzeug/0.8.3 Python/2.7.2
    Date: Wed, 16 Oct 2013 15:22:14 GMT

next: :doc:`partial-response`

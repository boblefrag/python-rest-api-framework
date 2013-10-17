Using more than a single endpoint
=================================

So far we have only talk about single endoint. However, is it possible
and very easy to create multimple endpoints on a single REST API
Framework instance.

You may have noticed that you use the class WSGIDispatcher to launch
your instance. In developpement environnment it look like :

.. code-block:: python

        from werkzeug.serving import run_simple
        from rest_api_framework.controllers import WSGIDispatcher
        app = WSGIDispatcher([ApiApp])
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True

WSGIDispatcher take a list of app as a constructor. To add more
endpoint to your API you can write :

.. code-block:: python

    WSGIDispatcher([UserApp, EventApp])


each app will be available under the ressource name endpoint. For example

* /user/
* /event/



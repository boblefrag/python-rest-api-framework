"""
An app to test how to make API services with werkzeug

How it should work:

- describe your ressources
  - fields to be displayed
  - how fields should be displayed
  - etc...

- define global settings

  - pagination
  - authorization
  - authentication
  - throttling
  - etc..

"""

from base import Dispatcher
from datastore import PythonListDataStore
from api_views import ApiView

ressources = [
    {"name": "bob",
     "age": a,
     "id": a
     } for a in range(100)
    ]


class View(ApiView):
    """
    The main views of the application
    """
    pass


class ApiApp(Dispatcher, View):

    def __init__(self):
        urls = [
            ('/', 'index', ["GET", "POST"]),
            ('/<int:identifier>/', 'unique_uri', ["GET", "PUT", "DELETE"]),
            ]

        options = {"paginate_by": 20,
                   }
        self.datastore = PythonListDataStore(ressources, **options)
        super(ApiApp, self).__init__(urls)


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = ApiApp()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

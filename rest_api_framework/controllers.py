"""
Define base controller for your API.
"""
import json
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from abc import ABCMeta
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.exceptions import NotFound


class WSGIWrapper(object):
    """
    Base Wsgi application loader. WSGIWrapper is an abstract
    class. Herited by :class:`.ApiController` it make the class
    callable and implement the request/response process
    """

    __metaclass__ = ABCMeta

    def __call__(self, environ, start_response):
        """
        return the wsgi wrapper
        """
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        """
        instanciate a Request object, dispatch to the needed method,
        return a response
        """
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request):
        """
        Using the :class:`werkzeug.routing.Map` constructed by
        :meth:`.load_urls` call the view method with the request
        object and return the response object.
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, endpoint)(request, **values)
        except HTTPException, e:
            return e


class WSGIDispatcher(DispatcherMiddleware):
    """
    WSGIDispatcher take a list of :class:`.Controller` and mount them
    on their ressource mount point.
    basic syntax is:

    .. code-block:: python

       app = WSGIDispatcher([FirstApp, SecondApp])
    """

    def __init__(self, apps):
        endpoints = {}
        for elem in apps:
            endpoints["/{0}".format(elem.ressource["ressource_name"])] = elem()
        app = NotFound()
        mounts = endpoints
        super(WSGIDispatcher, self).__init__(app, mounts=mounts)


class ApiController(WSGIWrapper):
    """
    Inherit from :class:`.WSGIWrapper`
    implement the base API method. Should be inherited to create your own API
    """

    __metaclass__ = ABCMeta

    views = None

    def __init__(self, *args, **kwargs):
        super(ApiController, self).__init__(*args, **kwargs)

    def render_list(self, objs):
        for obj in objs:
            obj['ressource_uri'] = "/{0}/{1}/".format(
                self.ressource['ressource_name'],
                obj['id'])
        return objs

    def index(self, request):
        """
        The root url of your ressources. Should present a list of
        ressources if method is GET.
        Should create a ressource if method is POST
        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        if self.auth is set call
        :meth:`.authentication.Authentication.check_auth`

        :return: :meth:`.get_list` if request.method is GET,
                 :meth:`.create` if request.method is POST
        """
        if hasattr(self, "authorization"):
            self.authorization.check_auth(request)

        if request.method == "GET":
            return self.get_list(request)

        if request.method == "POST":
            return self.create(request)

    def paginate(self, request):
        """
        A pagination example. Feel free to implement your own

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """

        if hasattr(self, "pagination"):
            offset, count, request_kwargs = self.pagination.paginate(request)
        else:
            offset, count = None
        filters = request_kwargs
        return self.view['response_class'](
            self.render_list(
                self.datastore.get_list(offset=offset,
                                        count=count,
                                        **filters)
                ),
            status=200)

    def get_list(self, request):
        """
        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        return self.paginate(request)

    def unique_uri(self, request, identifier):
        """
        Retreive a unique object with his URI.
        Act on it accordingly to the Http verb used.

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        if hasattr(self, "authorization"):
            self.authorization.check_auth(request)

        if request.method == "GET":
            return self.get(request, identifier)
        if request.method == "PUT":
            return self.update(request, identifier)
        if request.method == "DELETE":
            return self.delete(request, identifier)

    def get(self, request, identifier):
        """
        Return an object or 404

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        obj = self.datastore.get(identifier=identifier)

        return self.view['response_class'](
            obj,
            status=200)

    def create(self, request):
        """
        Create a new object in the datastore

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        try:
            data = json.loads(request.data)
        except:
            raise BadRequest()
        response = self.datastore.create(data)
        return self.view['response_class'](
            headers={"location": str(response)}, status=201)

    def update(self, request, identifier):
        """
        Update an object in the datastore

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`

        """
        obj = self.datastore.get(identifier=identifier)
        obj = self.datastore.update(obj, json.loads(request.data))
        return self.view['response_class'](
            obj,
            status=200)

    def delete(self, request, identifier):
        """
        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        self.datastore.delete(identifier=identifier)
        return self.view['response_class'](status=200)


class Controller(ApiController):
    """
    The main views of the application
    """

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.urls = [
            ('/', 'index', self.controller['list_verbs']),
            ('/<int:identifier>/',
             'unique_uri',
             self.controller['unique_verbs']),
            ]
        self.url_map = self.load_urls()
        self.datastore = self.ressource['datastore'](
            self.ressource['ressource'],
            self.ressource['model'],
            **self.ressource.get('options', {})
            )
        if self.controller.get("options", None):
            self.make_options(self.controller["options"])

        super(Controller, self).__init__(*args, **kwargs)

    def load_urls(self):
        """
        :param urls: A list of tuple in the form (url(string),
                     view(string), permitted Http verbs(list))
        :type urls: list

        return a :class:`werkzeug.routing.Map`

        this method is automaticaly called by __init__ to build the
        :class:`.Controller` urls mapping
        """
        return Map(
            [
                Rule(pattern[0], endpoint=pattern[1], methods=pattern[2])
                for pattern in self.urls
                ]
            )

    def make_options(self, options):
        if options.get("pagination", None):
            self.pagination = options["pagination"]
        if options.get("authentication", None):
            self.authentication = options["authentication"]
        if options.get("authorization", None):
            if not hasattr(self, "authentication"):
                raise ValueError(
                    "Authorization option need an Authentication backend")
            self.authorization = options["authorization"](self.authentication)

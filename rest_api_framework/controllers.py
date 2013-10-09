import json
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from abc import ABCMeta, abstractmethod


class WSGIWrapper(object):
    """
    accept a request, return a response
    """

    __metaclass__ = ABCMeta

    def __call__(self, environ, start_response):
        """
        return the wsgi wrapper
        """
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)


class Dispatcher(object):
    """
    Given a set of urls,
    manage the urls mapping
    """

    __metaclass__ = ABCMeta

    def __init__(self, urls, *args, **kwargs):
        self.url_map = self.load_urls(urls)

    def load_urls(self, urls):
        """
        return a Map object containing urls mapping
        """
        return Map(
            [
                Rule(pattern[0], endpoint=pattern[1], methods=pattern[2])
                for pattern in urls
                ]
            )

    def dispatch_request(self, request):
        """
        Bind a request to a method
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, endpoint)(request, **values)
        except HTTPException, e:
            return e


class ApiController(WSGIWrapper, Dispatcher):
    """
    Handle the basic functionality of a Restful API
    """

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.auth = None
        if kwargs.get('authentication'):
            self.auth = kwargs['authentication']
        return super(ApiController, self).__init__(*args, **kwargs)

    def render_list(self, objs):
        for obj in objs:
            obj['ressource_uri'] = "/{0}/{1}/".format(self.ressource_name,
                                                  obj['id'])
        return objs

    def index(self, request):
        """
        The root url of your ressources. Should present a list of
        ressources if method is GET.
        Should create a ressource if method is POST
        """
        if self.auth:
            self.auth.check_auth(request)

        if request.method == "GET":
            return self.get_list(request)

        if request.method == "POST":
            return self.create(request)

    def paginate(self, request):
        """
        A pagination example. Feel free to implement your own
        """
        first_id = request.values.to_dict().get("first_id", 0)
        filters = request.values.to_dict()
        filters.pop("first_id", None)
        return self.response_class(
            self.render_list(
                self.datastore.get_list(start=first_id, **filters)),
            status=200)

    def get_list(self, request):
        return self.paginate(request)

    def unique_uri(self, request, identifier):
        """
        Retreive a unique object with his URI.
        Act on it accordingly to the Http verb used.
        """
        if self.auth:
            self.auth.check_auth(request)

        if request.method == "GET":
            return self.get(request, identifier)
        if request.method == "PUT":
            return self.update(request, identifier)
        if request.method == "DELETE":
            return self.delete(request, identifier)

    def get(self, request, identifier):
        """
        Return an object or 404
        """
        obj = self.datastore.get(identifier=identifier)

        return self.response_class(
            obj,
            status=200)

    def create(self, request):
        """
        Create a new object in the datastore
        """
        try:
            data = json.loads(request.data)
        except:
            raise BadRequest()
        response = self.datastore.create(data)
        return self.response_class(
            headers={"location": str(response)}, status=201)

    def update(self, request, identifier):
        """
        Update an object in the datastore
        """
        obj = self.datastore.get(identifier=identifier)
        obj = self.datastore.update(obj, json.loads(request.data))
        return self.response_class(
            obj,
            status=200)

    def delete(self, request, identifier):
        self.datastore.delete(identifier=identifier)
        return self.response_class(status=200)


class Controller(ApiController):
    """
    The main views of the application
    """

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        urls = [
            ('/{0}/'.format(self.ressource_name), 'index', self.list_verbs),
            ('/{0}/<int:identifier>/'.format(self.ressource_name),
             'unique_uri',
             self.unique_verbs),
            ]
        self.datastore = self.datastore(self.ressource,
                                        self.model,
                                        **self.options)

        super(Controller, self).__init__(urls, *args, **kwargs)

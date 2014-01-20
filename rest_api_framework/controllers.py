"""
Define base controller for your API.
"""
import json
from werkzeug.exceptions import BadRequest, NotImplemented
from werkzeug.wrappers import Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from abc import ABCMeta
from werkzeug.wsgi import DispatcherMiddleware


class WSGIWrapper(object):
    """
    Base Wsgi application loader. WSGIWrapper is an abstract
    class. Herited by :class:`.ApiController` it make the class
    callable and implement the request/response process
    """

    __metaclass__ = ABCMeta
    url_map = None
    view = None

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
        except HTTPException, error:
            return self.view(
                {"error": error.description},
                status=error.code)


class AutoDocGenerator(WSGIWrapper):
    """
    Auto generate a documentation endpoint for each endpoints registered.
    """
    def __init__(self, apps):
        from werkzeug.wrappers import Response
        self.apps = apps
        self.url_map = Map([
                Rule('/', endpoint='schema'),
                Rule('/<ressource>/', endpoint='ressource_schema')
                ])
        self.view = Response

    def schema(self, request):
        """
        Generate the schema url of each endpoints
        """
        response = {}
        for elem in self.apps:
            response[elem.ressource['ressource_name']] = {
                "list_endpoint": "/{0}/".format(
                    elem.ressource['ressource_name']),
                "allowed list_verbs": elem.controller["list_verbs"],
                "allowed unique ressource": elem.controller["unique_verbs"],
                "schema_endpoint": "/schema/{0}/".format(
                    elem.ressource["ressource_name"])
                }

        return self.view(json.dumps(response), mimetype="application/json")

    def ressource_schema(self, request, ressource):
        """
        Generate the main endpoint of schema. Return the list of all
            print app.datastore.modelendpoints available
        """
        app = [elem for elem in self.apps
               if elem.ressource['ressource_name'] == ressource]
        if app:
            app = app[0]
            response = app.ressource['model']().get_schema()
        else:
            raise NotFound
        return self.view(json.dumps(response), mimetype="application/json")


class WSGIDispatcher(DispatcherMiddleware):
    """
    WSGIDispatcher take a list of :class:`.Controller` and mount them
    on their ressource mount point.
    basic syntax is:

    .. code-block:: python

       app = WSGIDispatcher([FirstApp, SecondApp])
    """

    def __init__(self, apps):
        endpoints = {"/schema": self.make_schema(apps)}
        for elem in apps:
            endpoints["/{0}".format(elem.ressource["ressource_name"])] = elem()
        app = NotFound()
        mounts = endpoints
        super(WSGIDispatcher, self).__init__(app, mounts=mounts)

    def make_schema(self, apps):
        return AutoDocGenerator(apps)


class ApiController(WSGIWrapper):
    """
    Inherit from :class:`.WSGIWrapper`
    implement the base API method. Should be inherited to create your own API
    """

    __metaclass__ = ABCMeta

    view = None
    ressource = None
    authorization = None
    pagination = None
    datastore = None
    ratelimit = None
    formaters = None

    def __init__(self, *args, **kwargs):
        super(ApiController, self).__init__(*args, **kwargs)

    def render_list(self, objs):
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

        :return: :meth:`.ApiController.get_list` if request.method is GET,
                 :meth:`.ApiController.create` if request.method is POST
        """
        if request.method == "HEAD":
            verbs = list(
                set(
                    self.controller[
                        'list_verbs'] + self.controller['unique_verbs']))
            return self.view(
                headers={"Allow": ",".join(verbs)},
                status=200)

        if self.authorization:
            self.authorization.check_auth(request)
        if self.ratelimit:
            self.ratelimit.check_limit(request)

        if request.method == "GET":
            return self.get_list(request)

        elif request.method == "POST":
            return self.create(request)

        elif request.method == "PUT":
            return self.update_list(request)
        else:
            raise NotImplemented()

    def paginate(self, request):
        """
        invoke the Pagination class if the optional pagination has been set.
        return the objects from the datastore using datastore.get_list
        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """

        if self.pagination:
            offset, count, request_kwargs = self.pagination.paginate(request)
        else:
            offset, count = None, None
            request_kwargs = request.values.to_dict()
        filters = request_kwargs
        if self.formaters:
            for formater in self.formaters:
                filters = formater(self, filters)

        objs = self.datastore.get_list(offset=offset,
                                       count=count,
                                       **filters)
        if self.pagination:
            total = self.datastore.count(**filters)
            meta = self.pagination.get_metadata(count=count,
                                                offset=offset,
                                                total=total,
                                                **filters)
        else:
            meta = {"filters": {}}
            for k, v in filters.iteritems():
                meta["filters"][k] = v

        return self.view(objs=objs, meta=meta, status=200)

    def get_list(self, request):
        """
        On the base implemetation only return self.paginate(request).
        Placeholder for pre pagination stuff.

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
        if self.authorization:
            self.authorization.check_auth(request)
        if self.ratelimit:
            self.ratelimit.check_limit(request)

        if request.method == "GET":
            return self.get(request, identifier)
        elif request.method == "PUT":
            return self.update(request, identifier)
        elif request.method == "DELETE":
            return self.delete(request, identifier)
        else:
            raise NotImplemented()

    def get(self, request, identifier):
        """
        Return an object or 404

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        obj = self.datastore.get(identifier=identifier)
        return self.view(
            objs=obj,
            status=200)

    def create(self, request):
        """
        Try to load the data received from json to python, format each
        field if a formater has been set and call the datastore for
        saving operation. Validation will be done on the datastore side

        If creation is successfull, add the location the the headers
        of the response and render a 201 response with an empty body

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        try:
            data = json.loads(request.data)
        except:
            raise BadRequest()
        if self.formaters:
            for formater in self.formaters:
                data = formater(self, data)
        response = self.datastore.create(data)

        return self.view(
            headers={"location": "{0}/".format(str(response))}, status=201)

    def update_list(self, request):
        """
        Try to mass update the data.
        """
        response = self.datastore.update_list(request)
        return self.view(response, status=202)

    def update(self, request, identifier):
        """
        Try to retreive the object identified by the identifier.
        Try to load the incomming data from json to python.

        Call the datastore for update.

        If update is successfull, return the object updated with a
        status of 200

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`

        """
        obj = self.datastore.get(identifier=identifier)
        data = json.loads(request.data)
        if self.formaters:
            for formater in self.formaters:
                data = formater(self, data)

        try:
            obj = self.datastore.update(obj, data)
        except ValueError:
            raise BadRequest

        return self.view(
            objs=obj,
            status=200)

    def delete(self, request, identifier):
        """
        try to retreive the object from the datastore (will raise a
        NotFound Error if object does not exist) call the delete

        method on the datastore.

        return a response with a status code of 204 (NO CONTENT)

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        self.datastore.get(identifier=identifier)
        self.datastore.delete(identifier=identifier)
        return self.view(status=204)


class Controller(ApiController):
    """
    Controller configure the application.  Set all configuration
    options and parameters on the Controller, the View and the
    Ressource
    """

    controller = None

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

        self.view = self.view['response_class'](
            self.datastore.model,
            self.ressource["ressource_name"],
            **self.view.get('options', {}))

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
        """
        Make options enable Pagination, Authentication, Authorization,
        RateLimit and all other options an application need.
        """

        if options.get("formaters", None):
            self.formaters = options["formaters"]

        if options.get("pagination", None):
            self.pagination = options["pagination"]

        if options.get("authentication", None):
            self.authentication = options["authentication"]

        if options.get("ratelimit", None):
            if not hasattr(self, "authentication"):
                raise ValueError(
                    "RateLimit option need an Authentication backend")
            self.ratelimit = options["ratelimit"](self.authentication)

        if options.get("authorization", None):
            if not hasattr(self, "authentication"):
                raise ValueError(
                    "Authorization option need an Authentication backend")
            self.authorization = options["authorization"](self.authentication)

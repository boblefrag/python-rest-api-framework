"""
Define base controller for your API.
"""
from abc import ABCMeta
import json
import re
from collections import OrderedDict

from werkzeug.exceptions import BadRequest, NotImplemented
from werkzeug.wrappers import Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
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
        if hasattr(self, "authentication"):
            self.user = self.authentication.get_user(request)
        try:
            endpoint, values = adapter.match()
            return getattr(self, endpoint)(request, **values)
        except HTTPException, error:
            return self.view(
                {"error": error.description},
                status=error.code)


class AutoSporeGenerator(WSGIWrapper):
    def __init__(self, apps, name, base_url, version):
        from werkzeug.wrappers import Response
        self.apps = apps
        self.name = name
        self.base_url = base_url
        self.version = version

        self.url_map = Map([
            Rule('/', endpoint='spore'),
        ])
        self.view = Response

    def spore(self, request):
        method_trad = {"GET": {"index": "list",
                               "unique_uri": "get"},
                       "POST": {"index": "create"},
                       "PUT": {"unique_uri": "update"},
                       "DELETE": {"unique_uri": "delete"}
                       }
        URL_PLACEHOLDER = re.compile(r'<[a-zA-Z]*:?([a-zA-Z0-9_-]*)>')

        spore_doc = OrderedDict()
        spore_doc['name'] = self.name
        spore_doc['base_url'] = self.base_url or request.host_url
        spore_doc['version'] = self.version
        spore_doc['expected_status'] = [200]
        spore_doc['methods'] = OrderedDict()

        for Service in self.apps:
            service = Service()
            service_base_path = '/%s' % service.ressource['ressource_name']

            for url in service.urls:
                endpoint = '%s%s' % (service_base_path, url[0])

                service_path = URL_PLACEHOLDER.sub(':\g<1>', endpoint)
                service_params = URL_PLACEHOLDER.findall(endpoint)

                for method in url[2]:
                    view_info = OrderedDict(
                        path=service_path,
                        method=method,
                        formats=[service.view.render_format])
                    if service_params:
                        view_info['required_params'] = service_params

                    if 'ressource_description' in service.ressource:
                        view_info['description'] = service.ressource[
                            'ressource_description']

                    method_name = '{method}_{service}'.format(
                        method=method_trad[method][url[1]],
                        service=service.ressource['ressource_name'].lower())
                    spore_doc['methods'][method_name] = view_info
        return self.view(json.dumps(spore_doc), mimetype="application/json")


class HelloGenerator(WSGIWrapper):

    def __init__(self, name, version):
        self.name = name
        self.version = version
        from werkzeug.wrappers import Response
        self.url_map = Map([Rule('/', endpoint='hello')
                            ])
        self.view = Response

    def hello(self, request):
        response = {"version": self.version,
                    "name": self.name}
        return self.view(json.dumps(response), mimetype="application/json")


class AutoDocGenerator(WSGIWrapper):
    """
    Auto generate a documentation endpoint for each endpoints registered.
    """
    def __init__(self, apps):
        from werkzeug.wrappers import Response
        self.apps = apps

        self.url_map = Map([
            Rule('/', endpoint='schema'),
            Rule('/<ressource>/', endpoint='ressource_schema'),
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
                    elem.ressource["ressource_name"]
                )
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

    def __init__(self, apps, name='PRAF', version='devel',
                 base_url=None, formats=None, autodoc=True,
                 autospore=True, hello=True):
        if formats is None:
            formats = []
        endpoints = {}
        for elem in apps:
            endpoints["/{0}".format(elem.ressource["ressource_name"])] = elem()
        if not formats:
            formats = ["json"]
        if autodoc:
            endpoints["/schema"] = self.make_schema(apps)
        if autospore:
            endpoints["/spore"] = self.make_spore(apps, name, base_url,
                                                  version)
        if hello:
            endpoints["/"] = self.make_hello(name, version)

        app = NotFound()
        mounts = endpoints
        super(WSGIDispatcher, self).__init__(app, mounts=mounts)

    def make_schema(self, apps):
        return AutoDocGenerator(apps)

    def make_spore(self, apps, name, base_url, version):
        return AutoSporeGenerator(apps, name, base_url, version)

    def make_hello(self, name, version):
        return HelloGenerator(name, version)


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

        verb_available = {
            'GET': 'get_list',
            'POST': 'create',
            'PUT': 'update_list'
        }
        try:
            return getattr(self, verb_available[request.method])(request)
        except KeyError:
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

        verb_available = {
            'GET': 'get',
            'PUT': 'update',
            'DELETE': 'delete'
        }
        try:
            return getattr(self,
                           verb_available[request.method])(request, identifier)
        except KeyError:
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

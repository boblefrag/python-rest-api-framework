"""
The minimum needed to take a response and render a response
- url mapper utility
- wsgiwrapper
"""

from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request, Response
import json


class JsonResponse(Response):
    """
    Just like a classic Response but render json everytime
    """
    def __init__(self, *args, **kwargs):
        return super(JsonResponse,
                     self).__init__(*args,
                                    mimetype="application/json",
                                    **kwargs)


class Dispatcher(object):
    """
    Given a set of urls,
    manage the urls mapping
    """

    def __init__(self, urls):
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

    def check_method(self, request, method):
        if request.method != method:
            return JsonResponse(
                json.dumps({
                    "error": "{0} not allowed with this URI".format(
                        request.method)
                    }),
                status=403)


class WSGIWrapper(object):
    """
    accept a request, return a response
    """
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

"""
The minimum needed to take a response and render a response
- url mapper utility
- wsgiwrapper
"""
from werkzeug.wrappers import Request, Response


class JsonResponse(Response):
    """
    Just like a classic Response but render json everytime
    """
    def __init__(self, *args, **kwargs):
        return super(JsonResponse,
                     self).__init__(*args,
                                    mimetype="application/json",
                                    **kwargs)


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

"""
The minimum needed to take a response and render a response
- url mapper utility
- wsgiwrapper
"""
from werkzeug.wrappers import Response


class JsonResponse(Response):
    """
    Just like a classic Response but render json everytime
    """
    def __init__(self, *args, **kwargs):
        return super(JsonResponse,
                     self).__init__(*args,
                                    mimetype="application/json",
                                    **kwargs)

"""
The minimum needed to take a response and render a response
- url mapper utility
- wsgiwrapper
"""
from werkzeug.wrappers import Response
import json


def add_ressource_uri(response, obj):
    obj["ressource_uri"] = "/{0}/{1}/".format(
        response.ressource_name,
        obj[response.model.pk_field.name])
    return obj


class JsonResponse(object):
    """
    Just like a classic Response but render json everytime
    """
    def __init__(self, model, ressource_name,
                 formaters=["add_ressource_uri"], **options):
        self.model = model
        self.ressource_name = ressource_name
        self.formaters = formaters
        if options:
            self.make_options(**options)

    def __call__(self, *args, **kwargs):

        if "objs" in kwargs:
            objs = self.format(kwargs.pop('objs'))
            return Response(json.dumps(objs),
                            mimetype="application/json",
                            **kwargs)
        else:
            return Response(*args,
                             mimetype="application/json",
                             **kwargs)

    def make_options(self, **options):
        print options

    def format(self, objs):

        if isinstance(objs, list):
            for elem in objs:
                for formater in self.formaters:
                    if hasattr(formater, '__call__'):
                        elem = formater(self, elem)
                    else:
                        elem = globals()[formater](self, elem)

        if isinstance(objs, dict):
            for formater in self.formaters:
                if hasattr(formater, '__call__'):
                    objs = formater(self, objs)
                else:
                    objs = globals()[formater](self, objs)

        return objs

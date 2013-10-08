"""
Handle the authentication process
"""
from werkzeug.exceptions import Unauthorized, NotFound


class ApiKeyAuth(object):
    """
    This authentication backend use an api key to authenticate and
    authorize users
    """
    def __init__(self, datastore):
        self.datastore = datastore

    def check_auth(self, request):
        """
        Check if a user is authorized to perform a particular action.
        """
        options = request.values.to_dict()
        if "apikey" in options:
            try:
                self.datastore.get(options['apikey'])
                return
            except NotFound:
                raise Unauthorized
        raise Unauthorized

"""
Handle the authentication process
"""
from werkzeug.exceptions import Unauthorized, NotFound


class Authorization(object):
    pass


class Authentication(object):
    pass


class ApiKeyAuthentication(Authentication):

    def __init__(self, datastore, **options):
        self.datastore = datastore

    def get_user(self, identifier):
        try:
            user = self.datastore.get(identifier)
            return user
        except NotFound:
            return None


class ApiKeyAuthorization(Authorization):
    """
    This authentication backend use an api key to authenticate and
    authorize users
    """
    def __init__(self, authentication, **options):
        self.authentication = authentication
        if options.get("authorized_method"):
            self.authorized_method = options.get("authorized_method")
        else:
            self.authorized_method = None

    def check_auth(self, request):
        """
        Check if a user is authorized to perform a particular action.
        """
        data = request.values.to_dict()
        if self.authorized_method and \
                request.method not in self.authorized_method:
            raise Unauthorized
        if "apikey" in data:
            if self.authentication.get_user(data['apikey']):
                return
            else:
                raise Unauthorized

        raise Unauthorized

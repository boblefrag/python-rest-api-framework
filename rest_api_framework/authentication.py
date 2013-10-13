"""
Handle the authentication process
"""
from werkzeug.exceptions import Unauthorized, NotFound


class Authorization(object):
    pass


class Authentication(object):

    def check_auth(self, request):
        """
        Return None if the request user is authorized to perform this
        action, raise Unauthorized otherwise

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        raise NotImplemented


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

    def check_auth(self, request):
        """
        Check if a user is authorized to perform a particular action.
        """
        data = request.values.to_dict()
        if "apikey" in data:
            if self.authentication.get_user(data['apikey']):
                return
            else:
                raise Unauthorized

        raise Unauthorized

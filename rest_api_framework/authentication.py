"""
Handle the authentication process
"""
from werkzeug.exceptions import Unauthorized, NotFound


class Authorization(object):
    """
    Check if an authenticated request can perform the given action.
    """

    def __init__(self, authentication):
        self.authentication = authentication

    def check_auth(self, request):
        """
        Return None if the request user is authorized to perform this
        action, raise Unauthorized otherwise

        :param request:
        :type request: :class:`werkzeug.wrappers.Request`
        """
        if self.authentication.get_user(request):
            return
        else:
            raise Unauthorized


class Authentication(object):
    """
    Manage the authentication of a request. Must implement the get_user method
    """
    def get_user(self, identifier):
        """
        Must return a user if authentication is successfull, None otherwise
        """
        raise NotImplementedError


class ApiKeyAuthentication(Authentication):
    """
    Authentication based on an apikey stored in a datastore.
    """

    def __init__(self, datastore, identifier="apikey"):
        self.identifier = identifier
        self.datastore = datastore

    def get_user(self, request):
        """
        return a user or None based on the identifier found in the
        request query parameters.
        """
        data = request.values.to_dict()
        if self.identifier in data:
            try:
                user = self.datastore.get(data[self.identifier])
                return user
            except NotFound:
                return None
        return None


class BasicAuthentication(Authentication):
    """
    Implement the Basic Auth authentication
    http://fr.wikipedia.org/wiki/HTTP_Authentification
    """
    def __init__(self, datastore):
        self.datastore = datastore

    def get_user(self, request):
        """
        return a user or None based on the Authorization: Basic header
        found in the request. login and password are Base64 encoded
        string : "login:password"
        """
        from base64 import b64decode
        auth = request.headers.get('Authorization: Basic', None)
        if auth:
            login, password = b64decode(auth).split(':')
            user = self.datastore.get_list(username=login, password=password)
            if user:
                return user[0]


class ApiKeyAuthorization(Authorization):
    """
    This authentication backend use an api key to authenticate and
    authorize users
    """

    pass

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

        raise NotImplementedError


class Authentication(object):
    """
    Manage the authentication of a request. Must implement the get_user method
    """
    def get_user(self, identifier):
        """
        Must return a user if authentication pass, None otherwise
        """
        raise NotImplementedError


class ApiKeyAuthentication(Authentication):
    """
    Authentication based on an apikey stored in a datastore.
    """
    def __init__(self, datastore):
        self.datastore = datastore

    def get_user(self, request):
        """
        return a user or None.
        """
        data = request.values.to_dict()
        identifier = "apikey"
        if identifier in data:
            try:
                user = self.datastore.get(data[identifier])
                return user
            except NotFound:
                return None
        return None


class ApiKeyAuthorization(Authorization):
    """
    This authentication backend use an api key to authenticate and
    authorize users
    """

    def check_auth(self, request):
        """
        Check if a user is authorized to perform a particular action.
        """
        if self.authentication.get_user(request):
            return
        else:
            raise Unauthorized

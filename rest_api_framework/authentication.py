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

    def get_user(self, identifier):
        """
        return a user or None.
        """
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

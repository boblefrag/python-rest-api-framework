"""
Handle the authentication process
"""
from werkzeug.exceptions import Unauthorized, NotFound


class ApiKeyAuth(object):
    """
    This authentication backend use an api key to authenticate and
    authorize users
    """
    def __init__(self, datastore, **options):
        self.datastore = datastore
        if options.get("authorized_method"):
            self.authorized_method = options.get("authorized_method")
        else:
            self.authorized_method = None

    def check_auth(self, request):
        """
        Check if a user is authorized to perform a particular action.
        """
        options = request.values.to_dict()
        if self.authorized_method and \
                request.method not in self.authorized_method:
            raise Unauthorized
        if "apikey" in options:
            try:
                self.datastore.get(options['apikey'])
                return
            except NotFound:
                raise Unauthorized
        raise Unauthorized

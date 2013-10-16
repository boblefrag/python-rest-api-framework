"""
Handle the rate limit option for a Controller.
"""
from werkzeug.exceptions import Unauthorized, HTTPException, NotFound
from werkzeug._internal import HTTP_STATUS_CODES
import time

HTTP_STATUS_CODES[429] = "Too Many Requests"


class TooManyRequest(HTTPException):
    """
    Implement the 429 status code (see
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html for details)
    """
    code = 429
    description = ("Rate Limit")


class RateLimit(object):
    """
    Rate limit a user depending on the datetime of the request, the
    number of previous requests and the rate-limit strategy
    """

    authentication = None

    def __init__(self, datastore, interval=6000, quota=100):
        self.datastore = datastore
        self.interval = interval
        self.quota = quota


    def __call__(self, authentication):
        self.authentication = authentication
        return self

    def check_limit(self, request):
        """
        Implment the rate-limit method should first authenticate the
        user, then check his rate-limit quota based on the request.
        If request is not rate-limited, should increment the
        rate-limit counter.

        Return None if the request is not rate-limited. raise
        HttpError with a 429 code otherwise
        """
        user = self.authentication.get_user(request)
        if user:
            user_pk = user[self.authentication.datastore.model.pk_field.name]
            try:
                quota = self.datastore.get_list(
                    **{self.datastore.model.pk_field.name: user_pk})[0]
            except IndexError:
                dico = {self.datastore.model.pk_field.name: user_pk,
                        "quota": self.quota,
                        "last_request": 0.0
                        }
                self.datastore.create(
                    dico
                    )
                quota = self.datastore.get_list(
                    **{self.datastore.model.pk_field.name: user_pk})[0]
            last_request = quota.get("last_request", None)
            if last_request:
                if time.time() < last_request + self.interval:
                    new_quota = quota.get('quota', self.quota) - 1
                    if new_quota == 0:
                        raise TooManyRequest()
                else:
                    new_quota = self.quota
            else:
                new_quota = quota.get('quota', self.quota) - 1

            self.datastore.update(quota,
                                  {'last_request': time.time(),
                                   'quota': new_quota}
                                  )
        else:
            raise Unauthorized

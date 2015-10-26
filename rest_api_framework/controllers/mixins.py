"""
Set of utilities to be used in specific cases
"""
import json
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict


class UserFiltered(object):
    """
    This mixin offers a way of filtering data on a per 'user' basis. A
    user is the dict returned by an authentication backend. You need
    to set what key you want your data to be filtered with in order to
    allow your datastore backend to return user based data. In a same
    way, you have to tell wich method should be user based.

    This controller is mainly a way to transmit a user to your
    backend. If you need to use more fine grained control on data
    access (like permissions) you should implement it in the datastore
    directly

    """
    def dispatch(self, matching_method, request, **values):
        if matching_method == self.unique_uri:
            verb_available = {
                'GET': 'get',
                'PUT': 'update',
                'DELETE': 'delete'
            }
        elif matching_method == self.index:
            verb_available = {
                'GET': 'get_list',
                'POST': 'create',
                'PUT': 'update_list'
            }
        if verb_available[request.method] in self.user_methods or \
        '*' in self.user_methods:
            if request.method in ["PUT", "POST"]:
                data = json.loads(request.data)
                data['user'] = self.user[
                    self.authentication.datastore.model.pk_field.name
                ] or None
                request.data = json.dumps(data)

            elif hasattr(request, "values"):
                request.values = CombinedMultiDict(request.values.dicts + [
                    ImmutableMultiDict(
                        {"user": self.user}
                    )])
        return super(UserFiltered, self).dispatch(matching_method, request,
                                                  **values)

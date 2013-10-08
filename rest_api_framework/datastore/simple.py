from .base import DataStore
from werkzeug.exceptions import NotFound


class PythonListDataStore(DataStore):
    """
    a datastore made of list of dicts
    """

    def get(self, identifier):
        """
        return an object matching the uri or None
        """
        for elem in self.data:
            if elem['id'] == identifier:
                return elem
        raise NotFound

    def filter(self, **kwargs):
        data = self.data
        for k, v in kwargs.iteritems():
            try:
                data = [elem for elem in data if elem[k] == v]
            except KeyError:
                pass
        return data

    def get_list(self, **kwargs):
        """
        return all the objects paginated if needed
        """
        start = kwargs.pop("start", None)
        data = self.filter(**kwargs)
        return self.paginate(data, start=start)

    def create(self, data):

        self.validate(data)
        obj = {}
        for k, v in data.iteritems():
            if k in self.description.iterkeys():
                obj[k] = v

        for field in self.description.iterkeys():
            if self.description[field]["type"] == "autoincrement":
                self.data.sort(lambda a, b: a[field] > b[field])
                last = self.data[-1][field]
                obj[field] = last + 1

        self.data.append(obj)
        return obj["id"]

    def update(self, obj, data):
        """
        Update a single object
        """
        # chek if the object already exists
        self.get(obj['id'])
        # check the fields to be updated
        self.validate_fields(data)
        # update the object
        for k, v in data.iteritems():
            obj[k] = v

        # save it in the datastore
        self.data[obj['id']] = obj
        # return the object
        return obj

    def delete(self, identifier):
        obj = self.get(identifier)
        self.data.remove(obj)

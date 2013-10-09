# -*- coding: utf-8 -*-

from werkzeug.exceptions import BadRequest


class DataStore(object):
    """
    define a source of data. Can be anything fron database to other
    api, files and so one
    """

    def __init__(self, data, **options):
        """
        Set the ressource datastore
        """
        self.data = data
        self.options = options
        self.description = options["description"]

    def get(self, identifier):
        """
        Should return a dictionnary representing the ressource matching the
        identifier or raise a NotFound exception.

        .. note::

           Not implemented by base DataStore class
        """
        raise NotImplemented

    def create(self, data):
        """
        data is a dict containing the representation of the
        ressource. This method should call
        :meth:`~.DataStore.validate`,
        create the data in the datastore and return the ressource
        identifier

        .. note::

           Not implemented by base DataStore class
        """
        raise NotImplemented

    def update(self, obj, data):
        """
        should be able to call :meth:`~.DataStore.get` to retreive the
        object to be updated, :meth:`~.DataStore.validate_fields` and
        return the updated object

        .. note::

           Not implemented by base DataStore class
        """
        raise NotImplemented

    def delete(self, identifier):
        """
        should be able to validate the existence of the object in the
        ressource and remove it from the datastore

        .. note::

           Not implemented by base DataStore class
        """
        raise NotImplemented

    def get_list(self, **kwargs):
        """
        This method is called each time you want a set of data.
        Data could be paginated and filtered.
        Should call :meth:`~.DataStore.filter`
        and return :meth:`~.DataStore.paginate`

        .. note::

           Not implemented by base DataStore class
        """
        raise NotImplemented

    def filter(self, **kwargs):
        """
        should return a way to filter the ressource according to
        kwargs.  It is not mandatory to actualy retreive the
        ressources as they will be paginated just after the filter
        call. If you retreive the wole filtered ressources you loose
        the pagination advantage. The point here is to prepare the
        filtering. Look at SQLiteDataStore.filter for an example.

        .. note::

           Not implemented by base DataStore class
        """
        raise NotImplemented

    def paginate(self, data, **kwargs):
        """
        Paginate sould return all the object if no pagination options
        have been set or only a subset of the ressources if pagination
        options exists.
        """
        start = 0
        end = self.options.get('paginate_by', None)
        if "start" in kwargs:
            start = int(kwargs['start'])
            end = start + self.options['paginate_by']
        elif "end" in kwargs:
            end = int(kwargs['end'])
            start = end - int(kwargs['end'])

        return data[start:end]

    def validate(self, data):
        """
        Check if data send are valide for objec creation. Validate
        Chek that each required fields are in data and check for their
        type too.

        Used to create new ressources
        """

        if not isinstance(data, dict):
            raise BadRequest()
        for k, v in self.description.iteritems():
            if self.description[k]['required']:
                if not k in data or \
                        not isinstance(data[k],
                                       self.description[k]['type']
                                       ):
                    raise BadRequest()

    def validate_fields(self, data):
        """
        Validate only some fields of the ressource.
        Used to update existing objects
        """
        if not isinstance(data, dict):
            raise BadRequest()
        for k, v in data.iteritems():
            if k not in self.description.iterkeys():
                raise BadRequest()
            elif not isinstance(v, self.description[k]["type"]):
                raise BadRequest()

"""
Handle the Pagination for a Controller.
"""


class Pagination(object):
    """
    The base implementation of Pagination.
    __init__ define max, offset and count.
    """
    def __init__(self, max_result,
                 offset_key="offset",
                 count_key="count"):

        self.max = max_result
        self.offset_key = offset_key
        self.count_key = count_key

    def paginate(self, request):
        """
        return an offset, a count and the request kwargs without
        pagination parameters
        """
        request_kwargs = request.values.to_dict()
        offset = int(request_kwargs.pop(self.offset_key, 0))
        count = int(request_kwargs.pop(self.count_key, self.max))
        if count > self.max:
            count = self.max
        return offset, count, request_kwargs

    def get_metadata(self, total=0, offset=0, count=0, **filters):
        meta = {self.offset_key: offset,
                self.count_key: count,
                "total_count": total,
                "filters": {}
                }
        for k, v in filters.iteritems():
            meta["filters"][k] = v
        if offset == 0:
            meta['previous'] = "null"
        else:
            meta["previous"] = offset - count
        if meta["previous"] < 0:
            meta["previous"] = 0
        if meta['previous'] != "null":
            meta["previous"] = "?{0}={1}".format(self.offset_key,
                                                 meta["previous"])

        meta["next"] = offset + count
        if meta["next"] > total:
            meta["next"] = "null"
        if meta['next'] != "null":
            meta["next"] = "?{0}={1}".format(self.offset_key,
                                                 meta["next"])
        return meta

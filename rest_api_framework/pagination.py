"""
Handle the Pagination for a Controller.
"""


class Pagination(object):
    """
    The base implementation of Pagination.
    """
    def __init__(self, max_result,
                 offset_key="offset",
                 count_key="count"):

        self.max = max_result
        self.offset_key = offset_key
        self.count_key = count_key

    def paginate(self, request):
        request_kwargs = request.values.to_dict()
        offset = int(request_kwargs.pop(self.offset_key, 0))
        count = int(request_kwargs.pop(self.count_key, self.max))
        if count > self.max:
            count = self.max
        return offset, count, request_kwargs

from common.request import WaldurConnection, InvalidTokenException

# separator for string format
sep = "~"


class RequestData(object):
    """
    Object for holding request data and executing the request.
    """

    def __init__(self,
                 method=None,
                 endpoint=None,
                 parameters=None
                 ):

        if endpoint is None:
            raise ValueError("endpoint must be set for request")

        if method is None:
            method = 'GET'

        if parameters is None:
            parameters = {}

        self.need_values = []
        for key, value in parameters.items():
            if value is None:
                self.need_values.append(key)

        self.endpoint = endpoint
        self.method = method
        self.parameters = parameters
        self.token = None
        self.sep = sep

    def set_token(self, token):
        self.token = token

    def request(self):
        # todo figure out how to get this programmatically
        api_url = "https://api.etais.ee/api/"

        if self.token is None:
            raise InvalidTokenException

        waldur = WaldurConnection(
            api_url=api_url,
            token=self.token
        )

        response = waldur.query(
            method=self.method,
            endpoint=self.endpoint,
            data=self.parameters
        )

        return response

    def to_string(self):
        res = "REQUEST" \
              + self.sep \
              + self.method \
              + self.sep \
              + self.endpoint \
              + self.sep

        for key, value in self.parameters.items():
            res += str(key) + "=" + str(value) + self.sep

        return res.strip(self.sep)

    @staticmethod
    def from_string(string):
        tokens = string.strip(sep).split(sep)
        print(str(tokens))

        method = tokens[1]
        endpoint = tokens[2]
        parameters = {}
        for i in range(3, len(tokens)):
            item = tokens[i].split("=")
            parameters[item[0]] = item[1]

        print(method)
        print(endpoint)
        print(str(parameters))
        return RequestData(method, endpoint, parameters)


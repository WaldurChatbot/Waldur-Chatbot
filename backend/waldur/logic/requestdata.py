from common.request import WaldurConnection, InvalidTokenException
from logging import getLogger
log = getLogger(__name__)
# separator for string format
sep = "~"


class RequestData(object):
    """
    Object for holding request data and executing the request.


    Possible requests:
    Get projects for user
        GET
        services
        -

    Get services for user
        GET
        projects
        -

    todo add more

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
        return self  # builder pattern yo

    def request(self):
        # todo figure out how to get this programmatically
        api_url = "https://api.etais.ee/api/"

        if self.token is None:
            raise InvalidTokenException("Token is missing")

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

        method = tokens[1]
        endpoint = tokens[2]
        parameters = {}
        for i in range(3, len(tokens)):
            item = tokens[i].split("=")
            parameters[item[0]] = item[1]

        # todo implement lazy_hack_solution here

        return RequestData(method, endpoint, parameters)


class GetServicesRequest(RequestData):
    """
    GET projects
    """

    def __init__(self):
        super(GetServicesRequest, self).__init__(
            method='GET',
            endpoint='projects'
        )

    def request(self):
        response = super(GetServicesRequest, self).request()

        services = response[0]['services']

        names = []
        for service in services:
            names.append(service['name'])

        response_statement  = "Your organisation is using " + str(len(names)) + " services. "
        response_statement += "They are " + str(names)
        if str(len(names)) == 1:
            response_statement  = "Your organisation is using 1 service. "
            response_statement += "This service is " + str(names)

        return response_statement


class GetProjectsRequest(RequestData):

    def __init__(self):
        super(GetProjectsRequest, self).__init__(
            method='GET',
            endpoint='customers'
        )

    def request(self):
        response = super(GetProjectsRequest, self).request()

        projects = response[0]['projects']

        names = []
        for project in projects:
            names.append(project['name'])

        response_statement  = "You have " + str(len(names)) + " projects. "
        response_statement += "They are " + str(names)
        if str(len(names)) == 1:
            response_statement  = "You have 1 project. "
            response_statement += "The project is " + str(names)

        return response_statement


# todo make this less lazy
# should be able to parse class from string
def lazy_hack_solution(string):
    for request in [GetProjectsRequest(), GetServicesRequest()]:
        if string == request.to_string():
            return request
    raise Exception("Unknown request")
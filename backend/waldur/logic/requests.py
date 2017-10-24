from common.request import WaldurConnection, InvalidTokenException
from logging import getLogger
log = getLogger(__name__)

# separator for string format
sep = "~"


class Request(object):
    ID = None
    NAME = None
    """
    Base class for Requests to Waldur API, should not be instantiated directly.
    Subclass must override process() and if needed set_original()
    Subclasses must also have NAME and ID variables.
    """

    def __init__(self,
                 method=None,
                 endpoint=None,
                 parameters=None,
                 output='text'
                 ):

        if endpoint is None:
            raise ValueError("Endpoint must be set for request")

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
        self.output = output

        self.token = None
        self.original = None
        self.sep = sep

    def set_token(self, token):
        """
        :param token: Waldur API authentication token
        """
        self.token = token
        return self  # builder pattern yo

    def set_original(self, query):
        """
        Meant for requests that may need info from the original statement sent to backend.
        Subclass that needs original statement must override this method.
        :param query: original query sent to backend
        """
        self.original = query
        return self

    def request(self):
        """
        Method to query Waldur API.
        :return: response from Waldur API
        """
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

    def process(self):
        """
        Processes the Request, i.e. calls request() and formats the response.
        :return: Human readable response from Waldur API
        """
        raise NotImplementedError("Subclass must override this method")

    def to_string(self):  # todo do we need this?
        return "REQUEST" + self.sep + type(self).NAME

    @staticmethod
    def from_string(string):
        """
        Converts request from string to matching Request object
        :param string: request as string, ex. 'REQUEST~get_projects'
        :return: Matching Request object
        """
        tokens = string.strip(sep).split(sep)

        request_name = tokens[1]

        if request_name == GetServicesRequest.NAME:
            return GetServicesRequest()

        if request_name == GetProjectsRequest.NAME:
            return GetProjectsRequest()

        raise Exception("Unknown request")

    def marshall(self, data):
        return {
            'data': data,
            'type': self.output
        }


class GetServicesRequest(Request):
    ID = 1
    NAME = 'get_services'

    def __init__(self):
        super(GetServicesRequest, self).__init__(
            method='GET',
            endpoint='projects',
        )

    def process(self):
        response = self.request()

        services = response[0]['services']

        names = []
        for service in services:
            names.append(service['name'])

        response_statement  = "Your organisation is using " + str(len(names)) + " services. "
        response_statement += "They are " + str(names)
        if str(len(names)) == 1:
            response_statement  = "Your organisation is using 1 service. "
            response_statement += "This service is " + str(names)

        return self.marshall(response_statement)


class GetProjectsRequest(Request):
    ID = 2
    NAME = 'get_projects'

    def __init__(self):
        super(GetProjectsRequest, self).__init__(
            method='GET',
            endpoint='customers',
        )

    def process(self):
        response = self.request()

        projects = response[0]['projects']

        names = []
        for project in projects:
            names.append(project['name'])

        response_statement  = "You have " + str(len(names)) + " projects. "
        response_statement += "They are " + str(names)
        if str(len(names)) == 1:
            response_statement  = "You have 1 project. "
            response_statement += "The project is " + str(names)

        return self.marshall(response_statement)

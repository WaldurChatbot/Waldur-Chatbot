from chatterbot.logic import LogicAdapter
from common.request import WaldurConnection
from chatterbot.conversation.statement import Statement


class RequestLogicAdapter(LogicAdapter):
    """
    Abstract class for all logic adapters that query data from Waldur API
    """

    """
    Defines values (with default values) that a implementation adapter should have.
    """
    def __init__(self,
                 endpoint=None,
                 method=None,
                 parameters=None,
                 optional_parameters=None,
                 **kwargs
                 ):
        super(RequestLogicAdapter, self).__init__(**kwargs)

        if endpoint is None:
            raise ValueError("endpoint must be set for adapter")

        if method is None:
            method = 'GET'

        if parameters is None:
            parameters = {}

        if optional_parameters is None:
            optional_parameters = {}

        self.endpoint = endpoint
        self.method = method
        self.parameters = parameters
        self.optional_parameters = optional_parameters

    def can_process(self, statement):
        raise NotImplementedError("subclass must override can_process()")

    def process(self, statement):
        raise NotImplementedError("subclass must override process()")

    def request(self):
        # todo figure out how to get these programmatically
        api_url = "https://api.etais.ee/api/"
        token = "f5adefd4a5cd5757c552eac7992813c1ace7ec0b"

        waldur = WaldurConnection(
            api_url=api_url,
            token=token
        )

        response = waldur.query(
            method=self.method,
            endpoint=self.endpoint,
            data={**self.parameters, **self.optional_parameters}
        )

        return response


class GetProjectsLogicAdapter(RequestLogicAdapter):
    def __init__(self, **kwargs):
        super(GetProjectsLogicAdapter, self).__init__(
            method='GET',
            endpoint='customers'
        )

    def can_process(self, statement):
        words = ['my', 'projects']
        return all(x in statement.text.split() for x in words)

    def process(self, statement):
        response = self.request()
        projects = response[0]['projects']

        names = []
        for project in projects:
            names.append(project['name'])

        print("Yo, u have " + str(len(names)) + " projects")
        print("They are " + str(names))

        response_statement  = "You have " + str(len(names)) + " projects. "
        response_statement += "They are " + str(names)

        response_statement = Statement(response_statement)
        response_statement.confidence = 1

        return response_statement


from chatterbot.logic import LogicAdapter
from common.request import WaldurConnection, InvalidTokenException
from chatterbot.conversation.statement import Statement
from backend.__init__ import getLogger
from string import punctuation
log = getLogger(__name__)


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
        self.token = None

        self.confidence = None  # should be set by can_process() and sent out by process()

    def can_process(self, statement):
        raise NotImplementedError("subclass must override can_process()")

    def process(self, statement):
        raise NotImplementedError("subclass must override process()")

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
<<<<<<< Updated upstream
        self.confidence = 1
        return all(x in statement.text.split() for x in words)
=======
        return all(x in statement.text.translate(str.maketrans('','',punctuation)).split() for x in words)
>>>>>>> Stashed changes

    def process(self, statement):
        log.debug(str(statement))
        response = self.request()
        projects = response[0]['projects']

        names = []
        for project in projects:
            names.append(project['name'])

        response_statement  = "You have " + str(len(names)) + " projects. "
        response_statement += "They are " + str(names)

        response_statement = Statement(response_statement)
        response_statement.confidence = self.confidence

        return response_statement


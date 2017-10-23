from logging import getLogger
import re

from chatterbot.logic import LogicAdapter

from common.request import WaldurConnection, InvalidTokenException

log = getLogger(__name__)


#  deprecated
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
                 **kwargs
                 ):
        super(RequestLogicAdapter, self).__init__(**kwargs)

        if endpoint is None:
            raise ValueError("endpoint must be set for adapter")

        if method is None:
            method = 'GET'

        if parameters is None:
            parameters = {}

        self.endpoint = endpoint
        self.method = method
        self.parameters = parameters
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
            data=self.parameters
        )

        return response


class CreateVMRequestLogicAdapter(RequestLogicAdapter):

    def __init__(self):
        super(CreateVMRequestLogicAdapter).__init__(
            "<CHANGEME>",  # todo
            "POST"
        )

    def can_process(self, statement):
        regex = ""  # todo write regex or implement a better solution
        return re.match(regex, statement.text)

    def process(self, statement):
        pass  # todo implement
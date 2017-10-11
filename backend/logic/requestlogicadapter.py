from chatterbot.logic import LogicAdapter


"""
This class is intended as an interface for all request based logic adapters.
"""


class RequestLogicAdapter(LogicAdapter):
    def __init__(self, endpoint, method, parameters, optional_parameters, auth, allowed, **kwargs):
        super(RequestLogicAdapter, self).__init__(**kwargs)
        self.endpoint = endpoint
        self.method = method
        self.parameters = parameters
        self.optional_parameters = optional_parameters
        self.auth = auth
        self.allowed = allowed

    def can_process(self, statement):
        return False

    def process(self, statement):
        return statement

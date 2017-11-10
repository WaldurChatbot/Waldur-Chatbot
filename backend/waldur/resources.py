from logging import getLogger

from chatterbot.conversation import Statement
from flask_restful import Resource

from .parsers import query_parser, teach_parser
from .logic.requests import Request, text, InputRequest

log = getLogger(__name__)


class WaldurResource(Resource):
    """
    Parent class of all Waldur resources
    """
    def __init__(self, chatbot):
        """
        :param chatbot: Chatterbot bot
        """
        self.chatbot = chatbot
        self.response = None


class Query(WaldurResource):
    """
    Resource to get answers from the underlying Chatterbot
    """

    def __init__(self, chatbot, tokens_for_input):
        """
        :param tokens_for_input: dict of {token: InputRequest, ...}
        """
        super(Query, self).__init__(chatbot)
        self.tokens_for_input = tokens_for_input

        args = query_parser.parse_args()
        self.query = args.query
        self.token = args.token

    def post(self):
        """
        Entry point for POST /
        Gets a response statement from the bot
        :param: query - question/input for bot
        :param: token - Waldur API token
        :return: response, code
        """

        if self.token is not None and self.token in self.tokens_for_input:
            self._handle_input()
        else:
            self._handle_query()

        return self.response, 200

    def _handle_query(self):
        bot_response = str(self.chatbot.get_response(self.query))

        if bot_response.startswith("REQUEST"):
            req = Request\
                .from_string(bot_response)\
                .set_token(self.token)\
                .set_original(self.query)

            self.response = req.process()

            if isinstance(req, InputRequest):
                self.tokens_for_input[self.token] = req

        else:
            self.response = text(bot_response)

    def _handle_input(self):
        req = self.tokens_for_input[self.token]\
            .set_input(self.query)

        self.response = req.process()

        if not req.waiting_for_input:
            del self.tokens_for_input[self.token]


class Teach(WaldurResource):
    """
    Resource to give answers to the underlying Chatterbot
    """

    def __init__(self, chatbot):
        super(Teach, self).__init__(chatbot)

        args = teach_parser.parse_args()
        self.statement = args.statement
        self.previous_statement = args.previous_statement

    def post(self):
        """
        Entry point for POST /teach
        Teaches the bot that 'statement' is a valid response to 'previous_statement'
        :param: statement
        :param: previous_statement
        :return: response, code
        """

        self.chatbot.learn_response(Statement(self.statement), Statement(self.previous_statement))
        return text("Added '{}' as a response to '{}'".format(self.statement, self.previous_statement)), 200

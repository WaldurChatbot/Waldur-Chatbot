from logging import getLogger

from chatterbot.conversation import Statement
from flask_restful import Resource

from .parsers import query_parser, teach_parser
from .logic.requests import Request, text, InputRequest

log = getLogger(__name__)

# dict that holds all tokens that are in the middle of a request that needs input
# { token: Request, ... }
waiting_for_input = {}


class WaldurResource(Resource):

    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.response = None


class Query(WaldurResource):
    __name__ = ''

    def __init__(self, chatbot):
        super(Query, self).__init__(chatbot)
        self.parser = query_parser

    def post(self):
        """
        Entry point for POST /
        Gets a response statement from the bot
        :param: query - question/input for bot
        :param: token - Waldur API token
        :return: response, code
        """
        args = self.parser.parse_args()
        self.handle_query(args.query, args.token)

        return self.response, 200

    def handle_query(self, query, token=None):
        if token is not None and token in waiting_for_input:
            self.handle_input(query, token)
        else:
            self.set_response(query, token)

    def set_response(self, query, token=None):
        bot_response = str(self.chatbot.get_response(query))

        if bot_response.startswith("REQUEST"):
            req = Request\
                .from_string(bot_response)\
                .set_token(token)\
                .set_original(query)

            self.response = req.process()

            if isinstance(req, InputRequest):
                waiting_for_input[token] = req

        else:
            self.response = text(bot_response)

    def handle_input(self, input_query, token):
        req = waiting_for_input[token]

        req.set_input(input_query)

        self.response = req.process()

        if not req.waiting_for_input:
            del waiting_for_input[token]


class Teach(WaldurResource):

    def __init__(self, chatbot):
        super(Teach, self).__init__(chatbot)
        self.parser = teach_parser

    def post(self):
        """
        Entry point for POST /teach
        Teaches the bot that statement 'statement' is good in response to 'in_response_to' statement
        :param: statement
        :param: in_response_to
        :return: response, code
        """
        args = self.parser.parse_args()
        self.handle_teach(args.statement, args.in_response_to)
        return self.response, 200

    def handle_teach(self, statement, in_response_to):
        self.chatbot.learn_response(Statement(statement), Statement(in_response_to))
        self.response = text("Added '{}' as a response to '{}'".format(statement, in_response_to))

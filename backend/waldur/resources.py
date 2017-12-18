import logging

from chatterbot.conversation import Statement
from flask_restful import Resource

from .nameparser import extract_names_regex
from .parsers import query_parser, teach_parser, auth_parser
from .logic.requests import Request, text, InputRequest, InvalidTokenError
from common.utils import obscure

log = logging.getLogger(__name__)


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
        self.code = 200


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
        self.token = None

        if args.Authorization is not None:
            if args.Authorization.startswith("token "):
                self.token = args.Authorization[6:]
            else:
                self.token = args.Authorization

        log.info(f"Query initialized with {{query: '{self.query}', token: '{obscure(self.token)}'}}")

        if log.isEnabledFor(logging.DEBUG):
            obscured_tokens = {obscure(x): self.tokens_for_input[x] for x in self.tokens_for_input}
            log.debug(f"Tokens waiting for input: {obscured_tokens}")

    def post(self):
        """
        Entry point for POST /
        Gets a response statement from the bot
        :param: query - question/input for bot
        :param: token - Waldur API token
        :return: response, code
        """
        try:
            if self.token is not None and self.token in self.tokens_for_input:
                self._handle_input()
            else:
                self._handle_query()
        except InvalidTokenError:
            self.response = dict(message='Invalid Waldur API token')
            self.code = 401

        log.info(f"Query response: {self.response} code: {self.code}")
        return self.response, self.code

    def _handle_query(self):

        # Todo: Make it look better
        names_excluded = self.query
        for x in extract_names_regex(self.query):
            for splitted in x.split():
                names_excluded = names_excluded.replace(splitted, "").strip()
                names_excluded = " ".join(names_excluded.split())
        
        bot_response = str(self.chatbot.get_response(names_excluded))
        log.debug(f"Bot response: '{bot_response}'")

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

        log.info(f"Teach initialized with {{statement: '{self.statement}', "
                 f"previous_statement: '{self.previous_statement}'}}")

    def post(self):
        """
        Entry point for POST /teach/
        Teaches the bot that 'statement' is a valid response to 'previous_statement'
        :param: statement
        :param: previous_statement
        :return: response, code
        """

        self.chatbot.learn_response(Statement(self.statement), Statement(self.previous_statement))
        return text(f"Added '{self.statement}' as a response to '{self.previous_statement}'"), 200


class Authenticate(Resource):
    """
    Resource to intermediate token to frontend
    Not very secure
    """

    def __init__(self, auth_tokens):
        """
        :param auth_tokens: dict of {user_id: token, ...}
        """
        self.auth_tokens = auth_tokens

    def post(self, user_id):
        """
        Entry point for POST /auth/<user_id>
        :param user_id: user_id to tie the token to
        :param: token from POST body
        :return: response, code
        """
        args = auth_parser.parse_args()

        log.info(f"token {obscure(args.token)} received for {user_id}")

        self.auth_tokens[user_id] = args.token

        return {'message': 'ok'}, 200

    def get(self, user_id):
        """
        Entry point for GET /auth/<user_id>
        :param user_id: user_id to get the token for
        :return: response, code
        """
        log.info(f"token asked for {user_id}")

        if user_id in self.auth_tokens:
            token = self.auth_tokens[user_id]
            del self.auth_tokens[user_id]
            return {'token': token}, 200
        else:
            return {'message': f"No token for {user_id}"}, 404

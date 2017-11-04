import traceback
from logging import getLogger

from chatterbot.conversation import Statement
from flask import jsonify, request, make_response
from flask_restful import Resource, reqparse

from common.request import InvalidTokenException
from .logic.requests import Request, text

log = getLogger(__name__)


INVALID_TOKEN_MESSAGE = text("Couldn't query Waldur because of invalid or missing token, please send valid token")
MISSING_QUERY_MESSAGE = text("Parameter 'query' missing from request")
MISSING_TEACH_MESSAGE = text("Request needs parameters 'statement' and 'in_request_to'")
SYSTEM_ERROR_MESSAGE  = text("Internal system error.")

# dict that holds all tokens that are in the middle of a request that needs input
# { token: Request, ... }
waiting_for_input = {}


class Query(Resource):
    __name__ = ''

    def __init__(self, chatbot):
        log.info("Initializing Query class")
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('query')
        self.parser.add_argument('token')
        self.chatbot = chatbot

    def post(self):
        try:
            log.info("IN:  " + str(request.json))
            args = self.parser.parse_args()
            query = args['query']
            token = args['token']

            response, code = self.handle_query(query, token)

        except InvalidTokenException as e:
            log.info("InvalidTokenException: " + str(e))
            response = INVALID_TOKEN_MESSAGE
            code = 401
        except Exception:
            for line in traceback.format_exc().split("\n"): log.error(line)
            response = SYSTEM_ERROR_MESSAGE
            code = 500

        response = self.format_response(response)
        log.info("OUT: " + str(response) + " code: " + str(code))
        return make_response(jsonify(response), code)

    def handle_query(self, query, token):
        if query is not None:
            if token is not None and token in waiting_for_input:
                return self.handle_input(query, token), 200
            else:
                return self.get_response(query, token), 200
        else:
            return MISSING_QUERY_MESSAGE, 400

    def get_response(self, query, token):
        bot_response = str(self.chatbot.get_response(query))

        if bot_response.startswith("REQUEST"):
            req = Request\
                .from_string(bot_response)\
                .set_token(token)\
                .set_original(query)

            response = req.process()

            if req.waiting_for_input:
                waiting_for_input[token] = req
            elif token in waiting_for_input:
                del waiting_for_input[token]

        else:
            response = bot_response

        return response

    def handle_input(self, input_query, token):
        req = waiting_for_input[token]

        req.set_input(input_query)

        response = req.process()

        if not req.waiting_for_input:
            del waiting_for_input[token]

        return response

    def format_response(self, response):
        if response is None:
            raise Exception("Response should not be None")

        if isinstance(response, dict):
            return [response]

        if isinstance(response, str):
            return [text(response)]

        return list(response)


class Teach(Resource):

    def __init__(self, chatbot):
        log.info("Initializing TeachBot class")
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('statement')
        self.parser.add_argument('in_response_to')
        self.chatbot = chatbot

    def post(self):
        try:
            log.info("IN:  " + str(request.json))
            args = self.parser.parse_args()
            statement = args['statement']
            in_response_to = args['in_response_to']

            if statement is not None and in_response_to is not None:
                self.chatbot.learn_response(Statement(statement), Statement(in_response_to))
                response = text('Added "{}" as a response to "{}"'.format(
                    statement,
                    in_response_to
                ))
                code = 200
            else:
                response = MISSING_TEACH_MESSAGE
                code = 400

        except Exception:
            for line in traceback.format_exc().split("\n"): log.error(line)
            response = SYSTEM_ERROR_MESSAGE
            code = 500

        log.info("OUT: " + str(response) + " code: " + str(code))
        return make_response(jsonify(response), code)

from logging import getLogger
import traceback

from flask import jsonify, request, make_response
from flask_restful import Resource, reqparse

from common.request import InvalidTokenException
from common.respond import marshall
from .logic.requests import Request

log = getLogger(__name__)

INVALID_TOKEN_MESSAGE = "Couldn't query Waldur because of invalid or missing token, please send valid token"
MISSING_QUERY_MESSAGE = "Parameter 'query' missing from request"
SYSTEM_ERROR_MESSAGE  = "Internal system error."


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
            print(query)
            print(token)

            if query is not None:
                log.debug("Getting response from chatterbot")
                response = self.get_response(query, token)
                response = marshall(str(response))
                code = 200
            else:
                response = marshall(MISSING_QUERY_MESSAGE)
                code = 400
        except InvalidTokenException as e:
            log.info("InvalidTokenException: " + str(e))
            response = marshall(INVALID_TOKEN_MESSAGE)
            code = 401
        except Exception:
            for line in traceback.format_exc().split("\n"): log.error(line)
            response = marshall(SYSTEM_ERROR_MESSAGE)
            code = 500

        log.info("OUT: " + str(response) + " code: " + str(code))
        return make_response(jsonify(response), code)

    def get_response(self, query, token):
        bot_response = str(self.chatbot.get_response(query))

        if bot_response.startswith("REQUEST"):
            return Request\
                .from_string(bot_response)\
                .set_token(token)\
                .set_original(query)\
                .process()
        else:
            return bot_response


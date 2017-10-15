from logging import getLogger
import traceback

from flask import jsonify, request, make_response
from flask_restful import Resource, reqparse

from common.request import InvalidTokenException
from common.respond import marshall

log = getLogger(__name__)


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
            self.add_token(token)
            if query is not None:
                log.debug("Getting response from chatterbot")
                response = self.chatbot.get_response(query)
                response = marshall(str(response))
                code = 200
            else:
                response = marshall("Parameter 'query' missing from request")
                code = 400
        except InvalidTokenException:
            log.info("Request sent with invalid token")
            response = marshall('Couldn\'t query Waldur because of invalid token, please send valid token')
            code = 401
        except Exception:
            for line in traceback.format_exc().split("\n"): log.error(line)
            response = marshall('Internal system error.')
            code = 500

        log.info("OUT: " + str(response) + " code: " + str(code))
        return make_response(jsonify(response), code)

    def add_token(self, token):
        log.debug("Adding token to all logic adapters")
        for adapter in self.chatbot.logic.get_adapters():
            if hasattr(adapter, 'set_token'):
                adapter.set_token(token)

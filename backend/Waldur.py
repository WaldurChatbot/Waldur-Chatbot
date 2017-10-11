import sys
import os
from common.respond import marshall
from common.request import MissingTokenException
from backend.__init__ import logging
from chatterbot import ChatBot
from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource, reqparse
from configparser import ConfigParser
import traceback

log = logging.getLogger(__name__)
# disable print, due to chatterbot
sys.stdout = open(os.devnull, 'w')


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
            query = self.parser.parse_args()['query']
            token = self.parser.parse_args()['token']
            add_token(self.chatbot, token)
            if query is not None:
                log.debug("Getting response from chatterbot")
                response = self.chatbot.get_response(query)
                response = marshall(str(response))
                code = 200
            else:
                response = marshall("Parameter 'query' missing from request")
                code = 400
        except MissingTokenException:  # why don't you work my dear except block
            log.info("Request sent with no token")
            response = marshall('Couldn\'t query Waldur because of missing token, please send token')
            code = 210  # this is a custom code, to which the client should react
        except Exception:
            for line in traceback.format_exc().split("\n"): log.error(line)
            response = marshall('Internal system error.')
            code = 500

        log.info("OUT: " + str(response) + " code: " + str(code))
        return make_response(jsonify(response), code)


def add_token(chatbot, token):
    log.debug("Adding token to all logic adapters")
    for adapter in chatbot.logic.get_adapters():
        if hasattr(adapter, 'set_token'):
            adapter.set_token(token)

def main():
    log.info("Initializing Backend")
    chatbot = ChatBot(
        'Waldur',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
        database='./chatterbotdb.sqlite3',
        logic_adapters=[
            'logic.requestlogicadapters.GetProjectsLogicAdapter',
            'chatterbot.logic.BestMatch',
        ]
    )

    log.info("Training chatterbot")
    chatbot.train("chatterbot.corpus.english.greetings")

    log.info("Creating Flask Api")
    app = Flask("Waldur")
    api = Api(app)
    api.add_resource(Query, '/', resource_class_kwargs={'chatbot': chatbot})

    log.info("Loading config")
    config = ConfigParser()
    config.read('../configuration.ini')
    port = config['backend']['port']

    log.info("Launching Backend")
    app.run(port=port)


if __name__ == '__main__':
    main()

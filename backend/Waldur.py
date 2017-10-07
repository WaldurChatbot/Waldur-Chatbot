import sys
import os
from __init__ import respond


import logging, logging.config, logging.handlers
from chatterbot import ChatBot
from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource, reqparse
from configparser import ConfigParser

logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)

log = logging.getLogger(__name__)

# disable print, due to chatterbot
sys.stdout = open(os.devnull, 'w')


class Query(Resource):
    __name__ = ''

    def __init__(self, chatbot):
        log.info("Initializing Query class")
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('query')
        self.chatbot = chatbot

    def post(self):
        try:
            log.info("IN:  " + str(request.json))
            query = self.parser.parse_args()['query']
            if query is not None:
                response = self.chatbot.get_response(query)
                response = respond.ok(str(response))
                code = 200
            else:
                response = respond.error("Parameter 'query' missing from request")
                code = 400
        except Exception as e:
            log.error(e)
            response = respond.error('System error.')
            code = 500

        log.info("OUT: " + str(response) + " code: " + str(code))
        return make_response(jsonify(response), code)


def main():
    log.info("Initializing Backend")
    chatbot = ChatBot(
        'Waldur',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
        database='./chatterbotdb.sqlite3'
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

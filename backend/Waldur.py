import sys
import os
sys.path.insert(0, '../')  # important for common import

import logging, logging.config, logging.handlers
from common import respond
from chatterbot import ChatBot
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from configparser import ConfigParser

logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)

log = logging.getLogger("Waldur")

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
            log.info("IN:  " + request.json)
            query = self.parser.parse_args()['query']
            if query is not None:
                response = self.chatbot.get_response(query)
                return jsonify(respond.ok(str(response))), 200
            else:
                return jsonify(respond.error("This url supports only POST with the argument 'query'")), 405
        except Exception as e:
            log.error(e)
            return jsonify(respond.error('System error.')), 500


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

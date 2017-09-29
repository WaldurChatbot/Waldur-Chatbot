import sys
import logging, logging.config, logging.handlers
sys.path.insert(0, '../')
from common import respond
from chatterbot import ChatBot
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from configparser import ConfigParser
from traceback import print_exc

logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)

log = logging.getLogger("Waldur")

class Query(Resource):
    __name__ = ''

    def __init__(self, chatbot):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('query')
        self.chatbot = chatbot

    def post(self):
        try:
            query = self.parser.parse_args()['query']
            if query is not None:
                response = self.chatbot.get_response(query)
                return jsonify(respond.ok(str(response)))
            else:
                return jsonify(respond.error("This url supports only POST with the argument 'query'"))
        except Exception:
            print_exc()
            return jsonify(respond.error('System error.'))


def main():
    log.info("Initializing Backend")
    chatbot = ChatBot(
        'Waldur',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
        database='./chatterbotdb.sqlite3'
    )

    chatbot.train("chatterbot.corpus.english.greetings")

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

from logging import getLogger
from os import path

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from flask import Flask, request, make_response, jsonify
from flask_restful import Api

from .corpus.list_training_data import waldur_list_corpus
from .resources import Query, Teach, Authenticate

log = getLogger(__name__)


def init_bot():
    log.info("Creating bot")
    return ChatBot(
        'Waldur',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
        database='./chatterbotdb.sqlite3',
        logger=log,
        logic_adapters=[
            'chatterbot.logic.BestMatch',
            {
                'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                'threshold': 0.55,
                'default_response': 'I am sorry, but I do not understand.'
            }
        ]
    )


def train_bot(chatbot):
    log.info("Training bot on chatterbot corpus")
    chatbot.train("chatterbot.corpus.english.greetings")

    log.info("Training bot on waldur corpus")
    waldur_corpus = path.join(path.dirname(path.abspath(__file__)), 'corpus')
    chatbot.train(waldur_corpus)

    chatbot.set_trainer(ListTrainer)
    for conversation in waldur_list_corpus:
        chatbot.train(conversation)

    return chatbot


def init_api(chatbot):
    log.info("Creating Flask api")

    class WaldurApi(Api):
        """
        Adds error logging to Api
        """
        def handle_error(self, e):
            log.exception(e)
            return super(WaldurApi, self).handle_error(e)

    api = WaldurApi(app=Flask(chatbot.name))

    @api.representation('application/json')
    def output_json(data, code, headers=None):

        if isinstance(data, dict):
            data = [data]
        else:
            data = list(data)

        resp = make_response(jsonify(data), code)
        resp.headers.extend(headers or {})
        return resp

    @api.app.before_request
    def log_request():
        log.info("IN:  {}".format(request))

    @api.app.after_request
    def log_response(response):
        log.info("OUT: {} data={}".format(response, response.get_data()))
        return response

    # dict that holds all tokens that are in the middle of a request that needs input
    # { token: Request, ... }
    tokens_for_input = {}

    # dict that holds tokens that are waiting for pickup by frontend
    # { user_id: token, ... }
    auth_tokens = {}

    api.add_resource(
        Query,
        '/',
        resource_class_kwargs={
            'chatbot': chatbot,
            'tokens_for_input': tokens_for_input
        }
    )
    api.add_resource(
        Teach,
        '/teach/',
        resource_class_kwargs={
            'chatbot': chatbot
        }
    )
    api.add_resource(
        Authenticate,
        '/auth/<user_id>',
        resource_class_kwargs={
            'auth_tokens': auth_tokens
        }
    )

    return api

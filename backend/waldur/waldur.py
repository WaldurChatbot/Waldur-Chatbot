from os import path
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from flask import Flask
from flask_restful import Api
from logging import getLogger
from .resources import Query
from .corpus.list_training_data import data

log = getLogger(__name__)

chatbot = ChatBot(
    'Waldur',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    database='./chatterbotdb.sqlite3',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
    ]
)

log.info("Training chatterbot")
chatbot.train("chatterbot.corpus.english.greetings")

corpus_path = path.join(path.dirname(path.abspath(__file__)), 'corpus')
chatbot.train(corpus_path)

chatbot.set_trainer(ListTrainer)
for conversation in data:
    chatbot.train(conversation)

log.info("Creating Flask app")
app = Flask("Waldur")

log.info("Creating Flask api")
api = Api(app)
api.add_resource(Query, '/', resource_class_kwargs={'chatbot': chatbot})


from chatterbot import ChatBot
from flask import Flask
from flask_restful import Api
from logging import getLogger
from .resources import Query

log = getLogger(__name__)

chatbot = ChatBot(
    'Waldur',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    database='./chatterbotdb.sqlite3',
    logic_adapters=[
        'backend.waldur.logic.requestlogicadapters.GetProjectsLogicAdapter',
        'backend.waldur.logic.requestlogicadapters.GetServicesLogicAdapter',
        'chatterbot.logic.BestMatch',
    ]
)

log.info("Training chatterbot")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("corpus.waldur")

log.info("Creating Flask app")
app = Flask("Waldur")

log.info("Creating Flask api")
api = Api(app)
api.add_resource(Query, '/', resource_class_kwargs={'chatbot': chatbot})


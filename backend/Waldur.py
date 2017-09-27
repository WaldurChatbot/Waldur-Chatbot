from chatterbot import ChatBot
from flask import Flask
from flask_restful import Api, Resource, reqparse

chatbot = ChatBot(
    'asd',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    database='./chatterbotdb.sqlite3'
)

chatbot.train("chatterbot.corpus.english")


app = Flask("Waldur")
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('query')


class Query(Resource):
    def post(self):
        query = parser.parse_args()['query']
        if query is not None:
            response = chatbot.get_response(query)
            return {'message': str(response)}
        else:
            return {'error': 'This url supports only POST with the argument query'}


class Hello(Resource):
    def get(self):
        return {'message': 'Hello World!'}



api.add_resource(Hello, '/hello')
api.add_resource(Query, '/')

app.run(port='4567')
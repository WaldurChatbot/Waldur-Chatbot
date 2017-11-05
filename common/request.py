from logging import getLogger
from requests import Session, Request
import json

log = getLogger(__name__)

INVALID_TOKEN_MESSAGE = "Needed token to query Waldur API. " \
                       "Token was either invalid or missing. " \
                       "Please send token like this '?<TOKEN>'"


class InvalidTokenException(Exception):
    pass


class BackendConnection(object):

    def __init__(self, backend_url):
        self.url = backend_url
        self.session = Session()
        self.tokens = {}  # tokens = { 'user_id': 'token', ... }

        self.last_bot_response = None
        self.last_query = None

    def add_token(self, user_id, token):
        self.tokens[user_id] = token

    def get_token(self, user_id):
        return None if user_id not in self.tokens else self.tokens.get(user_id)

    def get_response(self, message, user_id):
        log.info("IN:  {} {}".format(message, user_id))
        response = None

        prefix = message[:1]
        message = message[1:]

        if prefix == '!':
            response = self._handle_message(user_id, message)
        elif prefix == '?':
            response = self._handle_token(user_id, message)

        if isinstance(response, str):
            response = {
                'data': response,
                'type': 'text'
            }

        if not isinstance(response, list):
            response = [response]

        log.info("OUT: {} {}".format(response, user_id))
        return response

    def _handle_message(self, user_id, message):

        if message.lower() == 'thanks' or message.lower() == 'ty':  # todo a better solution
            self.teach(self.last_bot_response, self.last_query)

        try:
            response = self.query(
                message=message,
                token=self.get_token(user_id)
            )

            if len(response) == 1 and response[0]['type'] == 'text':
                self.last_query = message
                self.last_bot_response = response[0]['data']

        except InvalidTokenException:
            log.info("Needed token to query Waldur, asking user for token.")
            response = INVALID_TOKEN_MESSAGE

        return response

    def _handle_token(self, user_id, token):
        log.info("Received token from user " + str(user_id) + " with a length of " + str(len(token)))
        self.add_token(user_id, token)
        return "Thanks!"

    def request(self, method, url, data=None):
        request = Request(
            method,
            url,
            data=json.dumps(data)
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        log.info("Sending request: " + str(request.data))
        response = self.session.send(prepped)

        response_json = response.json()
        log.info("Received response: " + str(response_json))

        return response_json, response.status_code

    def query(self, message, token=None):
        response, status = self.request(
            'POST',
            self.url,
            data={
                'query': message,
                'token': token
            }
        )

        if status == 200:
            return response
        elif status == 401:
            raise InvalidTokenException
        else:
            raise Exception(response['data'])

    def teach(self, statement, in_response_to):
        response, status = self.request(
            'POST',
            self.url + '/teach',
            data={
                'statement': statement,
                'in_response_to': in_response_to
            }
        )

        if status == 200:
            return response
        else:
            raise Exception(response['message'])


class WaldurConnection(object):

    def __init__(self, api_url, token):

        if api_url[-1] != '/':
            api_url += '/'

        self.api_url = api_url
        self.token = token
        self.session = Session()

    def query(self, method, data, endpoint):
        if endpoint[-1] != '/':
            endpoint += '/'

        request = Request(
            method=method,
            url=self.api_url + endpoint,
            params=data
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        prepped.headers['Authorization'] = 'token ' + self.token
        response = self.session.send(prepped)

        response_json = response.json()

        if response.status_code == 200:
            return response_json
        elif response.status_code == 401:
            raise InvalidTokenException("Token is invalid - " + str(self.token))
        else:
            raise Exception(response_json['detail'])

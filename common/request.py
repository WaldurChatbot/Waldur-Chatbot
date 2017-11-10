from logging import getLogger
from requests import Session, Request
from .utils import obscure
import json

log = getLogger(__name__)


class InvalidTokenError(Exception):
    pass


class BackendConnection(object):

    INVALID_TOKEN_MESSAGE = "Needed token to query Waldur API. " \
                            "Token was either invalid or missing. " \
                            "Please send token like this '?<TOKEN>'"

    def __init__(self, backend_url):
        self.url = backend_url
        self.session = Session()
        self.tokens = {}  # tokens = { 'user_id': 'token', ... }

    def add_token(self, user_id, token):
        self.tokens[user_id] = token

    def get_token(self, user_id):
        return None if user_id not in self.tokens else self.tokens.get(user_id)

    def get_response(self, message, user_id):
        log.info("IN:  message={} user_id={}".format(message, user_id))
        response = None

        prefix = message[:1]
        message = message[1:]

        if prefix == '!':
            response = self._handle_message(user_id, message)
        elif prefix == '?':
            response = self._handle_token(user_id, message)

        log.info("OUT: response={} user_id={}".format(response, user_id))
        return response

    def _handle_message(self, user_id, message):

        try:
            response = self.query(
                message=message,
                token=self.get_token(user_id)
            )

        except InvalidTokenError:
            log.info("Needed token to query Waldur, asking user for token.")
            response = self.INVALID_TOKEN_MESSAGE

        return response

    def _handle_token(self, user_id, token):
        log.info("Received token {} from user {}".format(obscure(token), user_id))
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
            raise InvalidTokenError
        else:
            raise Exception(response['message'])

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
            raise InvalidTokenError("Token is invalid - " + str(self.token))
        else:
            raise Exception(response_json['detail'])

from common.__init__ import getLogger
from requests import Session, Request
import json

log = getLogger(__name__)


class InvalidTokenException(Exception):
    pass


class BackendConnection(object):

    def __init__(self, backend_url):
        self.url = backend_url
        self.session = Session()
        self.tokens = {}  # tokens = { 'user_id': 'token', ... }

    def add_token(self, user_id, token):
        self.tokens[user_id] = token

    def get_token(self, user_id):
        return None if user_id not in self.tokens else self.tokens.get(user_id)

    def get_response(self, message, user_id):
        log.info("IN: " + message)
        token = self.get_token(user_id)
        response = None

        log.debug("user_id: " + str(user_id) + " token: " + str(token))
        if message[:1] == '!':
            message = message[1:]
            try:
                response = self.query(
                    message=message,
                    token=token
                )
                response = response['message']
            except InvalidTokenException:
                log.info("Needed token to query Waldur, asking user for token.")
                response = "Needed token to query Waldur API. " \
                           "Token was either invalid or missing. " \
                           "Please send token like this '?<TOKEN>'"

        elif message[:1] == '?':
            log.info("Received token from user " + str(user_id) + " with a length of " + str(len(message[1:])))
            self.add_token(user_id, message[1:])
            response = "Thanks!"

        log.info("OUT: " + str(response))
        return response

    def query(self, message, token=None):
        request = Request(
            'POST',
            self.url,
            data=json.dumps({
                'query': message,
                'token': token
            })
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        log.info("Sending request: " + str(request.data))
        response = self.session.send(prepped)

        response_json = response.json()
        log.info("Received response: " + str(response_json))

        if response.status_code == 200:
            return response_json
        elif response.status_code == 401:
            raise InvalidTokenException
        else:
            raise Exception(response_json['message'])


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
            data=json.dumps(data)
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        prepped.headers['Authorization'] = 'token ' + self.token
        response = self.session.send(prepped)

        response_json = response.json()

        if response.status_code == 200:
            return response_json
        elif response.status_code == 401:
            raise InvalidTokenException
        else:
            raise Exception(response_json['detail'])

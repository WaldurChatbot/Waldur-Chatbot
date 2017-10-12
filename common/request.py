import __init__ as init
from requests import Session, Request
import json

log = init.getLogger(__name__)


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

    def query(self, q, token=None):
        request = Request(
            'POST',
            self.url,
            data=json.dumps({
                'query': q,
                'token': token
            })
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        log.info("Sending request: " + str(request.data))
        response = self.session.send(prepped)

        response_json = response.json()

        if response.status_code == 200:
            log.info("Received response: " + response_json['message'])
            return response_json
        elif response.status_code == 401:
            raise InvalidTokenException
        else:
            log.error("Received error response: " + response_json['message'])
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

import __init__ as init
from requests import Session, Request
import json

log = init.getLogger(__name__)


class MissingTokenException(Exception):
    pass


class BackendConnection(object):

    def __init__(self, backend_url):
        self.url = backend_url
        self.session = Session()
        self.token = None

    def set_token(self, token):
        self.token = token

    def query(self, q):
        request = Request(
            'POST',
            self.url,
            data=json.dumps({
                'query': q,
                'token': self.token
            })
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        log.info("Sending request: " + str(request.data))
        response = self.session.send(prepped)

        response_json = response.json()

        if response.status_code == 200:  # all responses in the range [200,300) are successes
            log.info("Received response: " + response_json['message'])
            return response_json
        elif response.status_code == 401:
            raise MissingTokenException
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
        else:
            raise Exception(response_json['detail'])

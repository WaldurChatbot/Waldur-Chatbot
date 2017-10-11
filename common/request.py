from requests import Session, Request
import json
import logging

logger = logging.getLogger(__name__)


class Connection(object):

    def __init__(self, url):
        self.url = url
        self.session = Session()

    def query(self, q):
        request = Request(
            'POST',
            self.url,
            data=json.dumps({'query': q})
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        logger.info("Sending request: " + str(request.data))
        response = self.session.send(prepped)

        response_json = response.json()

        if response.status_code == 200:
            logger.info("Received response: " + response_json['message'])
            return response_json
        else:
            logger.error("Received error response: " + response_json['message'])
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

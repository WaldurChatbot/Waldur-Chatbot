from logging import getLogger
from requests import Session, Request
from .utils import obscure
import json

log = getLogger(__name__)


class InvalidTokenError(Exception):
    pass


class BackendConnection(object):
    """
    Convenience class for python implementations of waldur chatbot.
    Provides methods for easily querying Waldur Chatbot Rest service.
    """

    INVALID_TOKEN_MESSAGE = "Needed token to query Waldur API. " \
                            "Token was either invalid or missing. " \
                            "Please send token like this '?<TOKEN>'"

    RECEIVED_TOKEN_MESSAGE = "Thanks!"

    def __init__(self, backend_url):
        self.url = backend_url
        self.session = Session()
        self.tokens = {}  # tokens = { 'user_id': 'token', ... }

    def add_token(self, user_id, token):
        self.tokens[user_id] = token

    def get_token(self, user_id):
        return None if user_id not in self.tokens else self.tokens.get(user_id)

    def get_response(self, message, user_id):
        """
        Get response to query from WaldurBot API
        :param message: message to get response to
        :param user_id: user id who queried, important for token
        :return: response from WaldurBot API
        """

        log.info(f"IN:  message={message} user_id={user_id}")

        try:
            response = self._query(
                message=message,
                token=self.get_token(user_id)
            )

        except InvalidTokenError:
            log.info("Needed token to query Waldur, asking user for token.")
            response = [{'type': 'text', 'data': self.INVALID_TOKEN_MESSAGE}]

        log.info(f"OUT: response={response} user_id={user_id}")
        return response

    def set_token(self, token, user_id):
        """
        Sets token for user.
        :param token: users token
        :param user_id: users id
        :return: response
        """
        log.info(f"Received token {obscure(token)} from user {user_id}")
        self.add_token(user_id, token)
        return [{'type': 'text', 'data': self.RECEIVED_TOKEN_MESSAGE}]

    def _request(self, method, url, data=None):
        request = Request(
            method,
            url,
            data=json.dumps(data)
        )

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        log.info(f"Sending request: {request.data}")
        response = self.session.send(prepped)

        response_json = response.json()
        log.info(f"Received response: {response_json}")

        return response_json, response.status_code

    def _query(self, message, token=None):
        response, status = self._request(
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
            raise Exception(response[0]['message'])

    def _teach(self, statement, in_response_to):
        response, status = self._request(
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
            raise Exception(response[0]['message'])


class WaldurConnection(object):
    """
    Class for querying Waldur API
    """

    def __init__(self, api_url, token):

        if api_url[-1] != '/':
            api_url += '/'

        self.api_url = api_url
        self.token = token.strip()
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
            raise InvalidTokenError()
        else:
            raise Exception(response_json['detail'])

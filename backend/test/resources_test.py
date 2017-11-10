from unittest import TestCase, main, mock, skip
from common.request import InvalidTokenError
from flask import json
from backend.waldur.waldur import init_api, init_bot


def return_ok(text):
    return "ok"


def return_REQUEST(text):
    return "REQUEST"


def raise_InvalidTokenError(text):
    raise InvalidTokenError


def raise_Exception(text):
    raise Exception


class WaldurTests(TestCase):

    def setUp(self):
        self.bot = init_bot()
        self.api = init_api(self.bot)
        self.app = self.api.app.test_client()
        self.endpoint = None

    def post(self, data=None):
        return self.app.post(self.endpoint, data=data)

    def assert_correct_response_form(self, response, type="text", error=False):
        self.assertTrue(isinstance(response, list))
        for item in response:
            if error:
                self.assertIn('message', item)
            else:
                self.assertIn('data', item)
                self.assertIn('type', item)
                self.assertEqual(type, item['type'])


class QueryTests(WaldurTests):

    def setUp(self):
        super(QueryTests, self).setUp()
        self.endpoint = "/"

    def test_request_with_no_data_response_error_400(self):
        response = self.post()

        self.assertEqual(400, response.status_code)
        self.assert_correct_response_form(json.loads(response.get_data()), error=True)

    @mock.patch('chatterbot.ChatBot.get_response', side_effect=return_ok)
    def test_request_with_no_token_is_ok(self, mock):
        response = self.post(
            data={
                'query': "asdf"
            }
        )

        self.assertEqual(200, response.status_code)
        self.assert_correct_response_form(json.loads(response.get_data()))

    @mock.patch('chatterbot.ChatBot.get_response', side_effect=raise_InvalidTokenError)
    def test_correct_response_on_invalid_token(self, mock):
        response = self.post(
            data={
                'query': 'qwer',
                'token': 'asdf'
            }
        )

        self.assertEqual(401, response.status_code)
        self.assert_correct_response_form(json.loads(response.get_data()), error=True)

    @mock.patch('chatterbot.ChatBot.get_response', side_effect=raise_Exception)
    def test_correct_response_on_system_error(self, mock):
        response = self.app.post(
            "/",
            data={
                'query': "irrelevant",
                'token': "asdqwe123"
            }
        )
        self.assertEqual(500, response.status_code)
        response = json.loads(response.get_data())
        self.assert_correct_response_form(response, error=True)

    @mock.patch('chatterbot.ChatBot.get_response', side_effect=return_ok)
    def test_good_request(self, mock):
        response = self.app.post(
            "/",
            data={
                'query': "hello",
                'token': "irrelevant token"
            }
        )
        self.assertEqual(200, response.status_code)
        response = json.loads(response.get_data())
        self.assert_correct_response_form(response)


class TeachTests(WaldurTests):

    def setUp(self):
        super(TeachTests, self).setUp()
        self.endpoint = "/teach/"

    def test_teach(self):
        statement = "Hello"
        previous_statement = "Hi"

        # Non-taught bot should mirror the statement back
        #self.assertEqual(previous_statement, str(self.bot.get_response(previous_statement)))

        response = self.post(
            data={
                'statement': statement,
                'previous_statement': previous_statement
            }
        )
        self.assert_correct_response_form(json.loads(response.get_data()))

        # Bot should know how to answer
        #self.assertEqual(statement, str(self.bot.get_response(previous_statement)))


if __name__ == '__main__':
    main()

from unittest import TestCase, main, mock
from common.request import InvalidTokenException
from flask import json
from backend.waldur.waldur import api


def mocked_chatbot_get_response_ok(text):
    return "ok"


def mocked_chatbot_get_response_bad_token(text):
    raise InvalidTokenException


class TestWaldur(TestCase):
    def setUp(self):
        self.app = api.app.test_client()

    def test_request_with_no_data_response_error_400(self):
        response = self.app.post("/")
        self.assertEqual(400, response.status_code)
        self.assertIn("message", json.loads(response.get_data()))

    @mock.patch('chatterbot.ChatBot.get_response', side_effect=mocked_chatbot_get_response_ok)
    def test_good_request(self, mock_get):
        response = self.app.post(
            "/",
            data={
                'query': "hello",
                'token': "irrelevant token"
            }
        )
        self.assertEqual(200, response.status_code)
        response = json.loads(response.get_data())
        self.assertIn('message', response)
        self.assertEqual("ok", response['message'])

    @mock.patch('chatterbot.ChatBot.get_response', side_effect=mocked_chatbot_get_response_bad_token)
    def test_bad_token(self, mock_get):
        response = self.app.post(
            "/",
            data={
                'query': "hello",
                'token': "bad token"
            }
        )
        self.assertEqual(401, response.status_code)
        response = json.loads(response.get_data())
        self.assertIn('message', response)
        self.assertIn("invalid", response['message'])
        self.assertIn("token", response['message'])


if __name__ == '__main__':
    main()

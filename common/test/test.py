from unittest import TestCase, main, mock
from ..request import BackendConnection, InvalidTokenError, WaldurConnection


class MockResponse:
    def __init__(self, data, code):
        self.data = data
        self.status_code = code

    def json(self):
        return self.data


def send_ok(request, *args, **kwargs):
    return MockResponse([{"data": "ok"}], 200)


def send_no_token(request, *args, **kwargs):
    return MockResponse([{"message": "No token"}], 404)


def send_invalid_token(request, *args, **kwargs):
    return MockResponse([{"message": "Invalid token"}], 401)


def send_error(request, *args, **kwargs):
    return MockResponse([{"message": "System error"}], 500)


def send_error_from_waldur_api(request, *args, **kwargs):
    return MockResponse({"detail": "System error"}, 500)


class BackendConnectionTests(TestCase):

    def setUp(self):
        self.conn = BackendConnection("test:4000", "asd:80")

    def test_can_add_and_get_token(self):
        user = 123
        token = 321
        self.conn.add_token(user, token)
        self.assertIn(user, self.conn.tokens)
        self.assertEqual(token, self.conn.tokens[user])
        self.assertEqual(token, self.conn.get_token(user))

    @mock.patch('requests.Session.send', side_effect=send_no_token)
    def test_none_if_no_token(self, mock_send):
        self.assertEqual(None, self.conn.get_token(222))

    @mock.patch('requests.Session.send', side_effect=send_ok)
    def test_query_responds_with_with_dict_on_correct_request(self, mock_send):
        response = self.conn._query("hello", "good_token")[0]
        self.assertDictEqual({"data": "ok"}, response)

    @mock.patch('requests.Session.send', side_effect=send_invalid_token)
    def test_query_responds_with_exception_on_invalid_token(self, mock_send):
        with self.assertRaises(InvalidTokenError):
            self.conn._query("hello", None)

    @mock.patch('requests.Session.send', side_effect=send_error)
    def test_query_responds_with_exception_on_error(self, mock_send):
        with self.assertRaises(Exception) as context:
            self.conn._query("hello", None)

        # assert that message is added to exception from response
        self.assertTrue("System error" in str(context.exception))


class WaldurConnectionTests(TestCase):

    def setUp(self):
        self.conn = WaldurConnection("https://url.api", "test token")

    @mock.patch('requests.Session.send', side_effect=send_ok)
    def test_query_responds_with_with_dict_on_correct_request(self, mock_send):
        response = self.conn.query("GET", {}, "test")[0]
        self.assertDictEqual({"data": "ok"}, response)

    @mock.patch('requests.Session.send', side_effect=send_invalid_token)
    def test_query_responds_with_exception_on_invalid_token(self, mock_send):
        with self.assertRaises(InvalidTokenError):
            self.conn.query("GET", {}, "test")

    @mock.patch('requests.Session.send', side_effect=send_error_from_waldur_api)
    def test_query_responds_with_exception_on_error(self, mock_send):
        with self.assertRaises(Exception) as context:
            self.conn.query("GET", {}, "test")

        # assert that message is added to exception from response
        self.assertTrue("System error" in str(context.exception))


if __name__ == '__main__':
    main()

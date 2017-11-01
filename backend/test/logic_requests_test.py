from unittest import TestCase, main, mock

from backend.waldur.logic.requests import GetServicesRequest
from backend.waldur.logic.requests import GetProjectsRequest


def mocked_query_services_0_names(method, data, endpoint):
    return create_services_response()


def mocked_query_services_1_name(method, data, endpoint):
    return create_services_response("test1")


def mocked_query_services_2_names(method, data, endpoint):
    return create_services_response("test1", "test2")


def create_services_response(*names):
    return [
        {
            'services': [
                {
                    'name': name
                } for name in names
            ]
        }
    ]


class TestGetServicesRequests(TestCase):
    def setUp(self):
        self.get_services = GetServicesRequest()
        self.get_services.set_token("asd")

    def assert_correct_response_format(self, response, type="text"):
        self.assertIn('data', response)
        self.assertIn('type', response)
        self.assertEqual(type, response['type'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_services_0_names)
    def test_get_services_0(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_services_1_name)
    def test_get_services_1(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_services_2_names)
    def test_get_services_2(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])
        self.assertIn("test2", response['data'])


def mocked_query_projects_0_names(method, data, endpoint):
    return create_projects_response()


def mocked_query_projects_1_name(method, data, endpoint):
    return create_projects_response("test1")


def mocked_query_projects_2_names(method, data, endpoint):
    return create_projects_response("test1", "test2")


def create_projects_response(*names):
    return [
        {
            'projects': [
                {
                    'name': name
                } for name in names
            ]
        }
    ]


class TestGetProjectsRequests(TestCase):
    def setUp(self):
        self.get_services = GetProjectsRequest()
        self.get_services.set_token("asd")

    def assert_correct_response_format(self, response, type="text"):
        self.assertIn('data', response)
        self.assertIn('type', response)
        self.assertEqual(type, response['type'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_projects_0_names)
    def test_get_services_0(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_projects_1_name)
    def test_get_services_1(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_projects_2_names)
    def test_get_services_2(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])
        self.assertIn("test2", response['data'])


if __name__ == '__main__':
    main()

from unittest import TestCase, main, mock

from backend.waldur.logic.requests import GetServicesRequest, InputRequest, QA
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


def returns_true(*args):
    return True


class TestInputRequestSingleQuestion(TestCase):
    QUESTION = "What's up?"
    ANSWERS  = ['y', 'yes']
    BAD_END_MSG = "how dare you"

    def setUp(self):
        self.ir = InputRequest([
            ('test', QA(self.QUESTION, self.ANSWERS))
        ], bad_end_msg=self.BAD_END_MSG)

    def test_set_get_input(self):
        self.ir.set_input("y")
        self.assertEqual("y", self.ir.input)
        self.assertEqual("y", self.ir.get_input())
        self.assertEqual(None, self.ir.input)
        self.assertEqual(None, self.ir.get_input())

    def test_handle_question_no_input(self):
        res = self.ir.handle_question()
        self.assertEqual(res, self.QUESTION)

    @mock.patch('backend.waldur.logic.requests.InputRequest.process', side_effect=returns_true)
    def test_handle_question_correct_input(self, mock):
        self.ir.set_input("y")
        # should reach process method, because we have no more questions after this one
        reached_process = self.ir.handle_question()
        self.assertTrue(reached_process)

        self.assertIn('test', self.ir.questions)
        # _evaluate must have been called, questions dict values should now have answers instead of questions
        self.assertEqual(self.ir.questions['test'], 'y')

    def test_handle_question_incorrect_input(self):
        self.ir.set_input("n")
        res = self.ir.handle_question()
        self.assertEqual(res, self.BAD_END_MSG)


class TestInputRequestMultipleQuestion(TestCase):
    I1 = "t1"
    Q1 = "q1"
    A1 = ['1']

    I2 = "t2"
    Q2 = "q2"
    A2 = ['2']

    I3 = "t3"
    Q3 = "q3"
    A3 = ['3']

    def setUp(self):
        self.ir = InputRequest([
            (self.I1, QA(self.Q1, self.A1)),
            (self.I2, QA(self.Q2, self.A2)),
            (self.I3, QA(self.Q3, self.A3)),
        ])

    @mock.patch('backend.waldur.logic.requests.InputRequest.process', side_effect=returns_true)
    def test_handle_all_questions(self, mock):
        question1 = self.ir.handle_question()
        self.assertEqual(question1, self.Q1)

        self.ir.set_input('1')
        question2 = self.ir.handle_question()
        self.assertEqual(question2, self.Q2)

        self.ir.set_input('2')
        question3 = self.ir.handle_question()
        self.assertEqual(question3, self.Q3)

        self.ir.set_input('3')
        reached_process = self.ir.handle_question()
        self.assertTrue(reached_process)

        self.assertEqual(self.ir.questions[self.I1], '1')
        self.assertEqual(self.ir.questions[self.I2], '2')
        self.assertEqual(self.ir.questions[self.I3], '3')


if __name__ == '__main__':
    main()

from unittest import TestCase, main, mock

from backend.waldur.logic.requests import *


class RequestTestCase(TestCase):
    def assert_correct_response_format(self, response, response_type="text"):
        self.assertIn('data', response)
        self.assertIn('type', response)
        self.assertEqual(response_type, response['type'])


def mocked_query_get_services_0_names(method, data, endpoint, parameters):
    return create_get_services_response()


def mocked_query_get_services_1_name(method, data, endpoint, parameters):
    return create_get_services_response("test1")


def mocked_query_get_services_2_names(method, data, endpoint, parameters):
    return create_get_services_response("test1", "test2")


def create_get_services_response(*names):
    return [
        {
            'name': name
        } for name in names
    ]


class TestGetServicesRequests(RequestTestCase):
    def setUp(self):
        self.get_services = GetServicesRequest()
        self.get_services.set_token("asd")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_services_0_names)
    def test_get_services_0(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_services_1_name)
    def test_get_services_1(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_services_2_names)
    def test_get_services_2(self, mock):
        response = self.get_services.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])
        self.assertIn("test2", response['data'])


def mocked_query_get_projects_0_names(method, data, endpoint, parameters):
    return create_get_projects_response()


def mocked_query_get_projects_1_name(method, data, endpoint, parameters):
    return create_get_projects_response(("org1", {"test1"}))


def mocked_query_get_projects_2_names(method, data, endpoint, parameters):
    return create_get_projects_response(("org2", {"test1", "test2"}))


def mocked_query_get_projects_2_organisations(method, data, endpoint, parameters):
    return create_get_projects_response(("org1", {"test1", "test2"}), ("org2", {"test3"}))


def mocked_query_get_projects_2_organisations_1_empty(method, data, endpoint, parameters):
    return create_get_projects_response(("org1", {"test1", "test2"}), ("org2", {}))


def mocked_query_use_case_3_regular_get_projects(method, data, endpoint, parameters):
    o_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    o_1_p_1 = "Waldur Chatbot testbed"
    o_1_p_2 = "2nd project"
    o_2 = "Waldur Maie"
    o_2_p_1 = "W-M project"
    return create_get_projects_response((o_1, (o_1_p_1, o_1_p_2)), (o_2, {o_2_p_1}))


def mocked_query_use_case_3_alt_a_get_projects(method, data, endpoint, parameters):
    o_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    o_1_p_1 = "Waldur Chatbot testbed"
    o_2 = "Waldur Maie"
    return create_get_projects_response((o_1, {o_1_p_1}), (o_2, {}))


def mocked_query_use_case_3_alt_b_get_projects(method, data, endpoint, parameters):
    o_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    return create_get_projects_response((o_1, {}))


def create_get_projects_response(*pairs):
    return [
        {
            'name': org,
            'projects': [
                {
                    'name': name
                } for name in names
            ]
        } for org, names in pairs
    ]


class TestGetProjectsRequests(RequestTestCase):
    def setUp(self):
        self.get_projects = GetProjectsRequest()
        self.get_projects.set_token("asd")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_projects_0_names)
    def test_get_projects_0(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_projects_1_name)
    def test_get_projects_1(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)
        self.assertIn("org1", response['data'])
        self.assertIn("test1", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_projects_2_names)
    def test_get_projects_2(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)
        self.assertIn("org2", response['data'])
        self.assertIn("test1", response['data'])
        self.assertIn("test2", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_projects_2_organisations)
    def test_get_projects_3(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)
        self.assertIn("org1", response['data'])
        self.assertIn("test1", response['data'])
        self.assertIn("test2", response['data'])
        self.assertIn("org2", response['data'])
        self.assertIn("test3", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_projects_2_organisations_1_empty)
    def test_get_projects_4(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)
        self.assertIn("org1", response['data'])
        self.assertIn("test1", response['data'])
        self.assertIn("test2", response['data'])
        self.assertNotIn("org2", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_3_regular_get_projects)
    def test_get_projects_5(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)
        correct_response = "You have 3 projects in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':\n    "
        correct_response += "Waldur Chatbot testbed\n    2nd project\nOrganisation 'Waldur Maie':\n    W-M project"
        self.assertEqual(correct_response, response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_3_alt_a_get_projects)
    def test_get_projects_6(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)
        correct_response = "You have 1 project in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':\n    "
        correct_response += "Waldur Chatbot testbed"
        self.assertEqual(correct_response, response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_3_alt_b_get_projects)
    def test_get_projects_7(self, mock):
        response = self.get_projects.process()
        self.assert_correct_response_format(response)
        self.assertEqual("You don't have any projects.", response['data'])


def mocked_query_get_vms_0_names(method, data, endpoint, parameters):
    return create_get_vms_response()


def mocked_query_get_vms_1_name(method, data, endpoint, parameters):
    return create_get_vms_response(("test1", "name1", ["1.1", "1.0"], ["1.2"]))


def mocked_query_get_vms_2_names(method, data, endpoint, parameters):
    return create_get_vms_response(("test1", "name1", ["1.1"], ["1.2"]), ("test2", "name2", ["2.1"], ["2.2"]))


def mocked_query_get_vms_no_ip(method, data, endpoint, parameters):
    return create_get_vms_response(("test1", "name1", [], []))


def mocked_query_use_case_12_regular_get_vms(method, data, endpoint, parameters):
    vm_1 = "WaldurChatbot Develop"
    cn_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_1_ip_1 = "193.40.11.164"
    vm_1_int_ip = "127.0.0.1"
    vm_2 = "WaldurChatbot Production"
    # cn_2 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_2_ip_1 = "193.40.11.175"
    vm_2_int_ip = "localhost"
    return create_get_vms_response((vm_1, cn_1, [vm_1_ip_1], [vm_1_int_ip]), (vm_2, cn_1, [vm_2_ip_1], [vm_2_int_ip]))


def mocked_query_use_case_12_alt_b_get_vms(method, data, endpoint, parameters):
    vm_1 = "WaldurChatbot Develop"
    cn_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_1_ip_1 = "193.40.11.164"
    vm_1_int_ip = "127.0.0.1"
    return create_get_vms_response((vm_1, cn_1, [vm_1_ip_1], [vm_1_int_ip]))


def mocked_query_use_case_12_alt_c_get_vms(method, data, endpoint, parameters):
    return create_get_vms_response()


def mocked_query_use_case_12_regular_two_ips_get_vms(method, data, endpoint, parameters):
    vm_1 = "WaldurChatbot Develop"
    cn_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_1_ip_1 = "193.40.11.164"
    vm_1_int_ip = "127.0.0.1"
    # cn_2 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_2 = "WaldurChatbot Production"
    vm_2_ip_1 = "193.40.11.175"
    vm_2_int_ip = "localhost"
    return create_get_vms_response((vm_1, cn_1, [vm_1_ip_1], [vm_1_int_ip]), (vm_2, cn_1, [vm_2_ip_1], [vm_2_int_ip]))


def mocked_query_use_case_12_alt_b_two_ips_get_vms(method, data, endpoint, parameters):
    vm_1 = "WaldurChatbot Develop"
    cn_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_1_ip_1 = "193.40.11.164"
    vm_1_ip_2 = "localhost"
    vm_1_int_ip = "127.0.0.1"
    return create_get_vms_response((vm_1, cn_1, [vm_1_ip_1, vm_1_ip_2], [vm_1_int_ip]))


def mocked_query_use_case_12_alt_b_no_ip_get_vms(method, data, endpoint, parameters):
    vm_1 = "WaldurChatbot Develop"
    cn_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_1_ip_1 = "None"
    vm_1_int_ip = "localhost"
    return create_get_vms_response((vm_1, cn_1, [vm_1_ip_1], [vm_1_int_ip]))


def mocked_query_use_case_12_alt_b_no_int_ip_get_vms(method, data, endpoint, parameters):
    vm_1 = "WaldurChatbot Develop"
    cn_1 = "Waldur Chatbot testbed (LTAT.05.005)"
    vm_1_ip_1 = "localhost"
    vm_1_int_ip = "None"
    return create_get_vms_response((vm_1, cn_1, [vm_1_ip_1], [vm_1_int_ip]))


def create_get_vms_response(*pairs):
    return [
        {
            'name': name,
            'customer_name': customer_name,
            'external_ips': external_ips,
            'internal_ips': internal_ips
        } for name, customer_name, external_ips, internal_ips in pairs
    ]


class TestGetVmsRequests(RequestTestCase):
    def setUp(self):
        self.get_vms = GetVmsRequest()
        self.get_vms.set_token("asd")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_vms_0_names)
    def test_get_vms_0(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_vms_1_name)
    def test_get_vms_1(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])
        self.assertIn("name1", response['data'])
        self.assertIn("1.1", response['data'])
        self.assertIn("1.0", response['data'])
        self.assertIn("1.2", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_vms_2_names)
    def test_get_vms_2(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])
        self.assertIn("name1", response['data'])
        self.assertIn("1.1", response['data'])
        self.assertIn("1.2", response['data'])
        self.assertIn("test2", response['data'])
        self.assertIn("name2", response['data'])
        self.assertIn("2.1", response['data'])
        self.assertIn("2.2", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_12_regular_get_vms)
    def test_get_vms_3(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        self.assertIn("You have 2 virtual machines in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':\n",
                      response['data'])
        c_response = "You have 2 virtual machines in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':" \
                     "\n    WaldurChatbot Production: localhost / 193.40.11.175" \
                     "\n    WaldurChatbot Develop: 127.0.0.1 / 193.40.11.164"
        c_response2 = "You have 2 virtual machines in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':" \
                      "\n    WaldurChatbot Develop: 127.0.0.1 / 193.40.11.164" \
                      "\n    WaldurChatbot Production: localhost / 193.40.11.175"
        self.assertTrue(c_response == response['data'] or c_response2 == response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_12_alt_b_get_vms)
    def test_get_vms_4(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        c_response = "You have 1 virtual machine in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':" \
                     "\n    WaldurChatbot Develop: 127.0.0.1 / 193.40.11.164"
        self.assertEqual(c_response, response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_12_alt_c_get_vms)
    def test_get_vms5(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        self.assertEqual("You don't have any virtual machines.", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_12_regular_two_ips_get_vms)
    def test_get_vms_6(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        self.assertIn("You have 2 virtual machines in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':\n"
                      , response['data'])
        c_response = "You have 2 virtual machines in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':" \
                     "\n    WaldurChatbot Develop: 127.0.0.1 / 193.40.11.164" \
                     "\n    WaldurChatbot Production: localhost / 193.40.11.175"
        c_response2 = "You have 2 virtual machines in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':" \
                      "\n    WaldurChatbot Production: localhost / 193.40.11.175\n    " \
                      "WaldurChatbot Develop: 127.0.0.1 / 193.40.11.164"
        self.assertTrue(c_response == response['data'] or c_response2 == response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_12_alt_b_two_ips_get_vms)
    def test_get_vms_7(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        correct_response = "You have 1 virtual machine in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':"
        correct_response += "\n    WaldurChatbot Develop: 127.0.0.1 / 193.40.11.164, localhost"
        self.assertEqual(correct_response, response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_vms_no_ip)
    def test_get_vms_8(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])
        self.assertIn("name1", response['data'])
        self.assertIn("- / -", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_12_alt_b_no_ip_get_vms)
    def test_get_vms_9(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        correct_response = "You have 1 virtual machine in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':"
        correct_response += "\n    WaldurChatbot Develop: localhost / None"
        self.assertEqual(correct_response, response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_use_case_12_alt_b_no_int_ip_get_vms)
    def test_get_vms_10(self, mock):
        response = self.get_vms.process()
        self.assert_correct_response_format(response)
        correct_response = "You have 1 virtual machine in total.\nOrganisation 'Waldur Chatbot testbed (LTAT.05.005)':"
        correct_response += "\n    WaldurChatbot Develop: None / localhost"
        self.assertEqual(correct_response, response['data'])


def mocked_query_get_organisations_0_names(method, data, endpoint, parameters):
    return create_get_organisations_response()


def mocked_query_get_organisations_1_name(method, data, endpoint, parameters):
    return create_get_organisations_response("test1")


def mocked_query_get_organisations_2_names(method, data, endpoint, parameters):
    return create_get_organisations_response("test1", "test2")


def create_get_organisations_response(*names):
    return [
        {
            'name': name
        } for name in names
    ]


class TestGetOrganisationsRequests(RequestTestCase):
    def setUp(self):
        self.get_organisations = GetOrganisationsRequest()
        self.get_organisations.set_token("asd")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_organisations_0_names)
    def test_get_organisations_0(self, mock):
        response = self.get_organisations.process()
        self.assert_correct_response_format(response)

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_organisations_1_name)
    def test_get_organisations_1(self, mock):
        response = self.get_organisations.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_organisations_2_names)
    def test_get_organisations_2(self, mock):
        response = self.get_organisations.process()
        self.assert_correct_response_format(response)
        self.assertIn("test1", response['data'])
        self.assertIn("test2", response['data'])


def mocked_query_get_total_cost_graph_org(method, data, endpoint, parameters):
    return mocked_query_get_total_cost_graph_response(('123', "Waldur Chatbot", "Meh"))


def mocked_query_get_total_cost_graph_empty(method, data, endpoint, parameters):
    return mocked_query_get_total_cost_graph_response()


def mocked_query_get_total_cost_graph_response(*names):
    return [
        {
            'uuid': uuid,
            'name': name,
            'customer': customer
        } for uuid, name, customer in names
    ]


class TestGetTotalCostGraphRequest(RequestTestCase):
    def setUp(self):
        self.get_graph = GetTotalCostGraphRequest()
        self.get_graph.set_token("asd")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_total_cost_graph_empty)
    def test_get_total_cost_of_organisation_0(self, mock):
        self.get_graph.set_original("organisation Waldur Maie")
        response = self.get_graph.process()
        self.assert_correct_response_format(response, "text")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_total_cost_graph_org)
    def test_get_total_cost_of_organisation_1(self, mock):
        self.get_graph.set_original("organisation Waldur Chatbot")
        response = self.get_graph.process()
        self.assert_correct_response_format(response, "graph")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_total_cost_graph_org)
    def test_get_total_cost_of_organisation_2(self, mock):
        self.get_graph.set_original("organisation Maie")
        response = self.get_graph.process()
        self.assert_correct_response_format(response, "text")
        c_response = "Sorry, I wasn't able to find an organisation with the name \"Maie\". " \
                     "Please check that an organisation with that name exists."
        self.assertEqual(c_response, response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_total_cost_graph_org)
    def test_get_total_cost_of_organisation_3(self, mock):
        self.get_graph.set_original("organisation waldur maie")
        response = self.get_graph.process()
        self.assert_correct_response_format(response, "text")
        self.assertNotIn("Waldur", response['data'])
        self.assertNotIn("Maie", response['data'])
        self.assertNotIn("maie", response['data'])
        self.assertNotIn("waldur", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_total_cost_graph_org)
    def test_get_total_cost_of_organisation_4(self, mock):
        self.get_graph.set_original("organisation waldur maie")
        response = self.get_graph.process()
        self.assert_correct_response_format(response, "text")
        c_response = "Sorry, I wasn't able to find an organisation's name in your request! " \
                     "Please write it out in capital case!"
        self.assertEqual(c_response, response['data'])


def mocked_query_get_org_ids_1_name(method, data, endpoint, parameters):
    return create_get_org_ids_response(("test1", "id1"))


def mocked_query_get_org_ids_2_names(method, data, endpoint, parameters):
    return create_get_org_ids_response(("test1", "id1"), ("test2", "id2"))


def create_get_org_ids_response(*pairs):
    return [
        {
            'name': name,
            'uuid': uuid
        } for name, uuid in pairs
    ]


class TestGetOrganisationsAndIdsRequests(RequestTestCase):
    def setUp(self):
        self.get_org_ids = GetOrganisationsAndIdsRequest()
        self.get_org_ids.set_token("asd")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_org_ids_1_name)
    def test_get_org_ids_1(self, mock):
        response = self.get_org_ids.process()
        self.assertIn('test1', response)
        self.assertIn('id1', response['test1'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_org_ids_2_names)
    def test_get_org_ids_2(self, mock):
        response = self.get_org_ids.process()
        self.assertIn('test1', response)
        self.assertIn('id1', response['test1'])
        self.assertIn('test2', response)
        self.assertIn('id2', response['test2'])


def mocked_query_get_clouds_by_org_no_org(method, data, endpoint, parameters):
    return create_get_clouds_by_org_response()


def mocked_query_get_clouds_by_org(method, data, endpoint, parameters):
    return create_get_clouds_by_org_response(("Waldur Maie", "id1"))


def create_get_clouds_by_org_response(*pairs):
    return [
        {
            'name': name,
            'uuid': uuid
        } for name, uuid in pairs
    ]


def mocked_query_get_clouds_by_org_subresponse_2():
    return create_get_clouds_by_org_subresponse("Waldur Chatbot", "Random Memes")


def mocked_query_get_clouds_by_org_subresponse_1():
    return create_get_clouds_by_org_subresponse("Waldur Chatbot")


def create_get_clouds_by_org_subresponse(*names):
    return [

            {'name': name}
        for name in names
    ]


class TestGetPrivateCloudsByOrganisationRequests(RequestTestCase):
    def setUp(self):
        self.get_cloud_by_org = GetPrivateCloudsByOrganisationRequest()
        self.get_cloud_by_org.set_token("asd")
        self.get_cloud_by_org.set_original("organisation Waldur Maie")

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_clouds_by_org_no_org)
    def test_get_cloud_by_org_0(self, mock):
        response = self.get_cloud_by_org.process()
        self.assertIn("\"Waldur Maie\"", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_clouds_by_org_no_org)
    def test_get_cloud_by_org_1(self, mock):
        response = self.get_cloud_by_org.process()
        c_response = "Sorry, I wasn't able to find an organisation with the name \"Waldur Maie\". " \
                     "Please check that an organisation with that name exists."
        self.assertEqual(c_response, response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_clouds_by_org_no_org)
    def test_get_cloud_by_org_2(self, mock):
        self.get_cloud_by_org.set_original("organisation waldur maie")
        response = self.get_cloud_by_org.process()
        self.assertNotIn("Waldur", response['data'])
        self.assertNotIn("Maie", response['data'])
        self.assertNotIn("maie", response['data'])
        self.assertNotIn("waldur", response['data'])

    @mock.patch('common.request.WaldurConnection.query', side_effect=mocked_query_get_clouds_by_org_no_org)
    def test_get_cloud_by_org_3(self, mock):
        self.get_cloud_by_org.set_original("organisation waldur maie")
        response = self.get_cloud_by_org.process()
        c_response = "Sorry, I wasn't able to find an organisation's name in your request! " \
                     "Please write it out in capital case!"
        self.assertEqual(c_response, response['data'])

    def test_get_cloud_by_org_4(self):
        response = self.get_cloud_by_org.subprocess(mocked_query_get_clouds_by_org_subresponse_1(), "Waldur Maie")
        self.assertIn("You have 1 private cloud in Waldur Maie.", response)
        c_response = "You have 1 private cloud in Waldur Maie.\nIts name is Waldur Chatbot."
        self.assertEqual(c_response, response)

    def test_get_cloud_by_org_5(self):
        response = self.get_cloud_by_org.subprocess(mocked_query_get_clouds_by_org_subresponse_2(), "Waldur Maie")
        self.assertIn("You have 2 private clouds in Waldur Maie.", response)
        c_response = "You have 2 private clouds in Waldur Maie.\nThey are:\n    Waldur Chatbot\n    Random Memes"
        c_response2 = "You have 2 private clouds in Waldur Maie.\nThey are:\n    Random Memes\n    Waldur Chatbot"
        self.assertTrue(c_response == response or c_response2 == response)


class QATests(TestCase):
    def test_simple(self):
        qa = QA("Sup?")
        self.assertTrue(qa.check("Answer"))
        self.assertEqual("Answer", qa.get_answer())

    def test_with_provided_answers(self):
        qa = QA("asd?", possible_answers=['y', 'n'])
        # Will return true, because no check_answer is supplied to QA
        self.assertTrue(qa.check("Answer"))
        self.assertEqual("Answer", qa.get_answer())

    def test_with_check_item(self):
        qa = QA("asd?", check_answer=lambda x, y: x if x == 'y' else None)
        self.assertFalse(qa.check("yes"))
        self.assertFalse(qa.check("asdfadfsf"))
        self.assertFalse(qa.check("Answer"))
        self.assertTrue(qa.check("y"))
        self.assertEqual("y", qa.get_answer())

    def test_with_provided_answers_and_check_item(self):
        qa = QA("asd?", possible_answers=['y', 'yes'], check_answer=lambda x, y: x if x in y else None)
        # Tie possible_answers to qa.found_possible_answers
        qa.get_possible_answers()
        self.assertFalse(qa.check("no"))
        self.assertTrue(qa.check("y"))
        self.assertTrue(qa.check("yes"))
        self.assertEqual("yes", qa.get_answer())

    def test_with_formatter(self):
        qa = QA("asd?",
                possible_answers=['y'],
                check_answer=lambda x, y: x if x in y else None,
                formatter=lambda x: "y/n")

        qa.get_possible_answers()
        self.assertFalse(qa.check("no"))
        self.assertTrue(qa.check("y"))
        self.assertEqual("y", qa.get_answer())
        self.assertIn("y/n", qa.get_formatted_possible_answers())


class CreateVMTests(RequestTestCase):
    def setUp(self):
        self.cvm = CreateVMRequest()

    def test_needs_token(self):
        with self.assertRaises(InvalidTokenError):
            self.cvm.process()

    def question_1(self):
        self.cvm.set_token("token")
        self.assert_correct_response_format(self.cvm.process())
        self.cvm.set_input("yes")
        self.assert_correct_response_format(self.cvm.process())
        self.assertEqual(True, self.cvm.parameters['continue'])

    def test(self):
        self.question_1()

        self.cvm.set_input("whatever")

        with mock.patch(
                'backend.waldur.logic.requests.possible_projects',
                side_effect=lambda token, parameters: {'value': 'test_url', 'settings_uuid': 'asdf'}
        ):
            #self.assert_correct_response_format(self.cvm.process())
            pass

        #self.assertEqual("whatever", self.cvm.parameters['name'])


if __name__ == '__main__':
    main()

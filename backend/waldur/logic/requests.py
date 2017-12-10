import itertools
import dateutil.parser
from collections import OrderedDict
from logging import getLogger

from common.request import WaldurConnection, InvalidTokenError
from ..nameparser import extract_names, getSimilarNames

log = getLogger(__name__)

# separator for string format
sep = "~"


def text(data):
    return {
        'type': 'text',
        'data': data
    }


def graph(data):
    return {
        'type': 'graph',
        'data': data
    }


class Request(object):
    """
    Base class for Requests to Waldur API, should not be instantiated directly.
    Subclass must override process()
    Subclasses must also have NAME and ID variables.
    """

    ID = None
    NAME = None
    HELP = None

    def __init__(self):
        self.token = None
        self.original = None

    def set_token(self, token):
        """
        :param token: Waldur API authentication token
        """
        self.token = token
        return self  # builder pattern yo

    def set_original(self, query):
        """
        Meant for requests that may need info from the original statement sent to backend.
        :param query: original query sent to backend
        """
        self.original = query
        return self

    def request(self, method, endpoint, parameters, data=None):
        """
        Method to query Waldur API.
        :return: response from Waldur API
        """
        # todo figure out how to get this programmatically
        api_url = "https://api.etais.ee/api/"

        self.check_token()

        waldur = WaldurConnection(
            api_url=api_url,
            token=self.token
        )

        response = waldur.query(
            method=method,
            endpoint=endpoint,
            parameters=parameters,
            data=data
        )

        return response

    def check_token(self, message="Token is missing"):
        if self.token is None:
            raise InvalidTokenError(message)

    def process(self):
        """
        Processes the Request, i.e. calls request() and formats the response.
        :return: Dict or tuple of dicts with 2 keys: 'type' and 'data'
                    'type' values:  'text' if data is string
                                    'graph' if data is dict from which a graph can be constructed
                 May return more than 1 dict as a tuple, in which case all dicts are processed sequentially by clienta
        """
        raise NotImplementedError("Subclass must override this method")

    def to_string(self):  # todo do we need this?
        return "REQUEST" + sep + type(self).NAME

    @staticmethod
    def from_string(string):
        """
        Converts request from string to matching Request object
        :param string: request as string, ex. 'REQUEST~get_projects'
        :return: Matching Request object
        """
        tokens = string.strip(sep).split(sep)

        request_name = tokens[1]

        for request in all_subclasses():
            if request.NAME == request_name:
                return request()

        raise Exception("Unknown request")


class SingleRequest(Request):
    def __init__(self,
                 method=None,
                 endpoint=None,
                 parameters=None,
                 data=None
                 ):
        super(SingleRequest, self).__init__()

        if endpoint is None:
            raise ValueError("Endpoint must be set for request")

        if method is None:
            method = 'GET'

        if parameters is None:
            parameters = {}

        if data is None:
            data = {}

        self.endpoint = endpoint
        self.method = method
        self.parameters = parameters
        self.data = data

    def send(self):
        return super(SingleRequest, self).request(
            method=self.method,
            endpoint=self.endpoint,
            parameters=self.parameters,
            data=self.data
        )

    def process(self):
        raise NotImplementedError("Subclass must override this method")


class QA(object):
    def __init__(self, question, possible_answers=None, check_answer=None, formatter=None):
        """
        :param question: Question to ask user.
        :param possible_answers: function that corresponds to
                                 def function(token: str, data) -> possible_answers
                                 data may be anything you want to
                                 returned possible_answers may be anything, it will be passed to check_answer
                                 this will be called before the user is sent the question
        :param formatter: callable that formats the possible_answers output to str
                          def function(possible_answers) -> str
                          returned value will be appended to the question that will be sent to user
                          this will be called after possible_answers func
        :param check_answer: callable to use when checking if selected answer is good. Corresponds to
                             def function(answer: str, possible_answers) -> answer
                             returned answer will be added to InputRequest parameters as answer to question
                             if returned answer is None, then question will not be considered as answered
                             this will be called when user sends answer
        """
        self.question = question
        self.possible_answers = possible_answers
        self.check_answer = check_answer
        self.formatter = formatter

        self.found_possible_answers = None
        self.answer = None

    def get_possible_answers(self, token=None, parameters=None):
        """
        :param token: Waldur API token
        :param parameters: InputRequest.parameters
        :return: output of possible_answers function. If possible_answers not callable, then value of possible_answers
        """
        if not callable(self.possible_answers):
            val = self.possible_answers
            self.possible_answers = lambda x, y: val

        self.found_possible_answers = self.possible_answers(token, parameters)
        return self.found_possible_answers

    def get_formatted_possible_answers(self):
        """
        :return: found_possible_answers formatted with formatter. If no formatter supplied, then None
        """
        if not callable(self.formatter):
            val = self.formatter
            self.formatter = lambda x: val

        return self.formatter(self.found_possible_answers)

    def check(self, item):
        """
        :param item: item to be checked with check_answer. If no check_answer supplied, then check will return True
                     and answer will be set to item
        :return: True if good answer, False otherwise
        """
        if not callable(self.check_answer):
            self.check_answer = lambda x, y: x

        answer = self.check_answer(item, self.found_possible_answers)
        if answer is not None:
            self.answer = answer
            return True
        return False

    def is_waiting(self):
        return self.answer is None

    def get_answer(self):
        if self.is_waiting():
            raise Exception("Answer should not be None at this point")
        return self.answer

    def __str__(self):
        return f"QA{{Q:'{self.question}', A:'{self.answer}'}}"

    def __repr__(self):
        return self.__str__()


class InputRequest(Request):
    """
    Class intended for requests that may want to prompt user for info.
    """

    def __init__(self, data, bad_end_msg=None):
        """
        Init
        :param data: list of tuples: [(key,value),(key,value),...], value can be later accessed by self.parameters[key]
        :param bad_end_msg: message to send to client when some input was not ok.
        """
        super(InputRequest, self).__init__()

        self.waiting_for_input = True
        self.questions = OrderedDict(data)
        self.bad_end_msg = bad_end_msg
        self.parameters = dict()
        self.input = None
        self.current = None

        # Start with questioning
        self._next_question()

    def set_input(self, data):
        """
        Method to give input to Request object
        """
        self.input = data
        return self

    def _get_input(self):
        """
        Method to get input, input is set back to None after call
        :return: string input
        """
        if self.input is None:
            return None
        else:
            out = self.input.strip()
            self.input = None
            return out

    def _next_question(self):
        """
        Sets self.current to the next question
        """
        q = list(self.questions)
        if self.current is None:
            self.current = q[0]
            return

        i = q.index(self.current)

        if i + 1 >= len(q):
            self.current = None
        else:
            self.current = q[i + 1]

    def _end(self, done):
        """
        Ends the input asking portion and either sends a message for fail or calls implementing classes process method.
        :param done: boolean - whether all questions have been answered
        :return: messages to client
        """
        self.waiting_for_input = False
        if done:
            return type(self).process(self)
        else:
            return self.bad_end_msg

    def process(self):
        # bot needs token to know who to query
        self.check_token()
        if self.waiting_for_input:
            return self._handle_question()

        return None

    def _handle_question(self):
        """
        Handles current question, if waiting for answer -> asks, else continues to next question
        :return: message to client
        """
        i = self._get_input()

        if self.current is None:
            return self._end(True)

        question = self.questions[self.current]

        if question.is_waiting():
            if i is not None:
                if question.check(i):
                    self.parameters[self.current] = self.questions[self.current].get_answer()
                    self._next_question()
                    return self._handle_question()
                else:
                    return self._end(False)
            else:
                question.get_possible_answers(self.token, self.parameters)
                return question.question + " " + question.get_formatted_possible_answers()
        else:
            raise Exception("Should be at the next question at this point")


class GetOrganisationsRequest(SingleRequest):
    ID = 4
    NAME = 'get_organisations'

    def __init__(self):
        super(GetOrganisationsRequest, self).__init__(
            method='GET',
            endpoint='customers',
            parameters={
                "page_size": 100
            }
        )

    def process(self):
        response = self.send()

        organisations = [organisation['name'] for organisation in response]

        if len(organisations) > 1:
            response_statement = \
                "You are part of {n} organisations. " \
                "They are:\n    {organisations}" \
                .format(
                    n=len(organisations),
                    organisations="\n    ".join(organisations)
                )
        elif len(organisations) == 1:
            response_statement = \
                "You are part of 1 organisation. " \
                "The organisation is {organisation}" \
                .format(
                    organisation=organisations[0]
                )
        else:
            response_statement = "You you aren't part of any organisation."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetProjectsRequest(SingleRequest):
    ID = 2
    NAME = 'get_projects'

    def __init__(self):
        super(GetProjectsRequest, self).__init__(
            method='GET',
            endpoint='customers',
            parameters={
                "page_size": 100
            }
        )

    def process(self):
        response = self.send()

        len_all = 0
        statement = ""
        for organisation in response:
            names = [project['name'] for project in organisation['projects']]
            len_all += len(names)
            if len(names) > 0:
                statement += "\nOrganisation '" + organisation['name'] + "':\n    " + "\n    ".join(names)

        if len_all > 0:
            if len_all == 1:
                response_statement = "You have 1 project in total."
            else:
                response_statement = "You have " + str(len_all) + " projects in total."
            response_statement += statement
        else:
            response_statement = "You don't have any projects."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetServicesRequest(SingleRequest):
    ID = 1
    NAME = 'get_services'

    def __init__(self):
        super(GetServicesRequest, self).__init__(
            method='GET',
            endpoint='services',
            parameters={
                "page_size": 100
            }
        )

    def process(self):
        response = self.send()

        services = set([service['name'] for service in response])

        if len(services) >= 1:
            response_statement = \
                "You have access to {n} service providers. " \
                "They are:\n    {services}" \
                .format(
                    n=len(services),
                    services="\n    ".join(services)
                )
        elif len(services) == 1:
            response_statement = \
                "You have access to 1 service provider. " \
                "This service is {service}." \
                .format(
                    service=services[0]
                )
        else:
            response_statement = "You dont have access to any service providers."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetServicesByOrganisationRequest(SingleRequest):
    ID = 6
    NAME = 'get_services_by_organisation'

    def __init__(self):
        super(GetServicesByOrganisationRequest, self).__init__(
            method='GET',
            endpoint='services',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_organisations = extract_names(self.original)

        if len(extracted_organisations) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out capital case!"
        else:
            most_similar = getSimilarNames(extracted_organisations, organisations)
            if most_similar == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + extracted_organisations[0] + "\". Please check that an " \
                                                                    "organisation with that name exists."
            else:

                self.parameters["customer"] = organisations_with_uuid[most_similar]
                response = self.send()

                service_names = set([service['name'] for service in response])

                if len(service_names) > 1:
                    response_statement = \
                        "You have access to {n} service providers in {similar}.\n" \
                        "They are:\n    {services}" \
                        .format(
                            n=len(service_names),
                            similar=most_similar,
                            services="\n    ".join(service_names)
                        )
                elif len(service_names) == 1:
                    response_statement = \
                        "You have access to 1 service provider in {similar}.\n" \
                        "This service is {service}." \
                        .format(
                            similar=most_similar,
                            service=service_names[0]
                        )
                else:
                    response_statement = "You don't have access to any service providers in " + most_similar + ". "
        return {
            'data': response_statement,
            'type': 'text'
        }


class GetServicesByProjectAndOrganisationRequest(SingleRequest):
    ID = 14
    NAME = 'get_services_by_project_and_organisation'

    def __init__(self):
        super(GetServicesByProjectAndOrganisationRequest, self).__init__(
            method='GET',
            endpoint='projects',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_names = extract_names(self.original)
        project_name = extracted_names[:1]
        organisation_name = extracted_names[1:]

        if len(extracted_names) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's nor project's name in your request! " \
                                 "Please write it out in capital case!"
        elif len(organisation_name) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar_organisation = getSimilarNames(organisation_name, organisations)
            if most_similar_organisation == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + organisation_name[0] + "\". Please check that an " \
                                                              "organisation with that name exists."
            else:

                secondreq = GetProjectsAndIdsByOrganisationRequest()
                secondreq.token = self.token
                secondreq.parameters["customer"] = organisations_with_uuid[most_similar_organisation]
                projects_with_uuid = secondreq.process()
                projects = [x for x in projects_with_uuid]

                most_similar_project = getSimilarNames(project_name, projects)

                if most_similar_project == "":
                    response_statement = "Sorry, I wasn't able to find a project with the name \"" \
                                         + project_name[0] + "\". Please check that a " \
                                                             "project with that name exists."

                else:

                    self.endpoint += "/" + str(projects_with_uuid[most_similar_project]) + "/"

                    response = self.send()

                    service_names = set([service['name'] for service in response["services"]])

                    if len(service_names) > 1:
                        response_statement = \
                            "You have access to {n} service providers in project {similar_project} of organisation " \
                            "{similar_organisation}.\nThey are:\n    {services}" \
                            .format(
                                n=len(service_names),
                                similar_project=most_similar_project,
                                similar_organisation=most_similar_organisation,
                                services="\n    ".join(service_names)
                            )
                    elif len(service_names) == 1:
                        response_statement = \
                            "You have access to 1 service provider in project {similar_project} of organisation " \
                            "{similar_organisation}.\nThis service is {service}." \
                            .format(
                                similar_project=most_similar_project,
                                similar_organisation=most_similar_organisation,
                                service=service_names[0]
                            )
                    else:
                        response_statement = "You don't have access to any service providers in project " + \
                                             most_similar_project + " of organisation " + most_similar_organisation \
                                             + ". "
        return {
            'data': response_statement,
            'type': 'text'
        }


class GetVmsRequest(SingleRequest):
    ID = 3
    NAME = 'get_vms'

    def __init__(self):
        super(GetVmsRequest, self).__init__(
            method='GET',
            endpoint='openstacktenant-instances',
            parameters={
                "page_size": 100
            }
        )

    def process(self):
        response = self.send()

        len_all = 0
        statement = ""
        organisations = sorted(response, key=lambda k: k['customer_name'])
        organisations = itertools.groupby(organisations, lambda vm: vm['customer_name'])
        for organisation, vms in organisations:
            names = {
                vm['name'] + ": " + ("-" if len(vm['internal_ips']) == 0 else ", ".join(vm['internal_ips'])) + " / " +
                ("-" if vm['external_ips'] == None or len(vm['external_ips']) == 0 else ", ".join(vm['external_ips'])) for vm in vms}
            len_all += len(names)
            if len(names) > 0:
                statement += "\nOrganisation '" + organisation + "':\n    " + "\n    ".join(names)

        if len_all > 0:
            if len_all == 1:
                response_statement = "You have 1 virtual machine in total."
            else:
                response_statement = "You have " + str(len_all) + " virtual machines in total."
            response_statement += statement
        else:
            response_statement = "You don't have any virtual machines."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetVmsByOrganisationRequest(SingleRequest):
    ID = 8
    NAME = 'get_vms_by_organisation'

    def __init__(self):
        super(GetVmsByOrganisationRequest, self).__init__(
            method='GET',
            endpoint='openstacktenant-instances',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_organisations = extract_names(self.original)

        if len(extracted_organisations) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar = getSimilarNames(extracted_organisations, organisations)
            if most_similar == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + extracted_organisations[0] + "\". Please check that an " \
                                                                    "organisation with that name exists."
            else:

                self.parameters["customer"] = organisations_with_uuid[most_similar]
                response = self.send()

                vm_names = {
                    vm['name'] + ": " + (
                        "-" if len(vm['internal_ips']) == 0 else ", ".join(vm['internal_ips'])) + " / " +
                    ("-" if vm['external_ips'] == None or  len(vm['external_ips']) == 0 else ", ".join(vm['external_ips'])) for vm in response}

                if len(vm_names) > 1:
                    response_statement = "You have " + str(len(vm_names)) + \
                                         " virtual machines in " + most_similar + ":\n    "
                    response_statement += "\n    ".join(vm_names)
                elif len(vm_names) == 1:
                    response_statement = "You have 1 virtual machine in " + most_similar + ".\n"
                    response_statement += "The virtual machine is:\n    "
                    response_statement += vm_names.pop()
                else:
                    response_statement = "You don't have any virtual machines in " + most_similar + ". "

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetVmsByProjectAndOrganisationRequest(SingleRequest):
    ID = 15
    NAME = 'get_vms_by_project_and_organisation'

    def __init__(self):
        super(GetVmsByProjectAndOrganisationRequest, self).__init__(
            method='GET',
            endpoint='openstacktenant-instances',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_names = extract_names(self.original)
        project_name = extracted_names[:1]
        organisation_name = extracted_names[1:]

        if len(extracted_names) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's nor project's name in your request! " \
                                 "Please write it out in capital case!"
        elif len(organisation_name) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar_organisation = getSimilarNames(organisation_name, organisations)
            if most_similar_organisation == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + organisation_name[0] + "\". Please check that an " \
                                                              "organisation with that name exists."
            else:

                secondreq = GetProjectsAndIdsByOrganisationRequest()
                secondreq.token = self.token
                secondreq.parameters["customer"] = organisations_with_uuid[most_similar_organisation]
                projects_with_uuid = secondreq.process()
                projects = [x for x in projects_with_uuid]

                most_similar_project = getSimilarNames(project_name, projects)

                if most_similar_project == "":
                    response_statement = "Sorry, I wasn't able to find a project with the name \"" \
                                         + project_name[0] + "\". Please check that a " \
                                                             "project with that name exists."

                else:

                    self.parameters["project"] = projects_with_uuid[most_similar_project]
                    response = self.send()

                    vm_names = {
                        vm['name'] + ": " + (
                            "-" if len(vm['internal_ips']) == 0 else ", ".join(vm['internal_ips'])) + " / " +
                        ("-" if vm['external_ips'] == None or  len(vm['external_ips']) == 0 else ", ".join(vm['external_ips'])) for vm in response}

                    if len(vm_names) > 1:
                        response_statement = "You have " + str(
                            len(vm_names)) + " virtual machines in project " + most_similar_project + \
                                             " of organisation " + most_similar_organisation + ":\n    "
                        response_statement += "\n    ".join(vm_names)
                    elif len(vm_names) == 1:
                        response_statement = "You have 1 virtual machine in project " + most_similar_project + \
                                             " of organisation " + most_similar_organisation + ":\n"
                        response_statement += "The virtual machine is:\n    "
                        response_statement += vm_names.pop()
                    else:
                        response_statement = "You don't have any virtual machines in project " + most_similar_project + " of organisation " + most_similar_organisation + ". "

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetPrivateCloudsRequest(SingleRequest):
    ID = 9
    NAME = 'get_private_clouds'

    def __init__(self):
        super(GetPrivateCloudsRequest, self).__init__(
            method='GET',
            endpoint='openstack-tenants',
            parameters={
                "page_size": 100
            }
        )

    def process(self):
        response = self.send()

        clouds = [cloud['name'] for cloud in response]

        len_all = 0
        statement = ""
        organisations = sorted(response, key=lambda k: k['customer_name'])
        organisations = itertools.groupby(organisations, lambda pc: pc['customer_name'])
        for organisation, pcs in organisations:
            names = [pc['name'] for pc in pcs]
            len_all += len(names)
            if len(names) > 0:
                statement += "\nOrganisation '" + organisation + "':\n    " + "\n    ".join(names)

        if len_all > 0:
            if len_all == 1:
                response_statement = "You have 1 private cloud."
            else:
                response_statement = \
                    "You have {n} private clouds in total.".format(n=len_all)
            response_statement += statement
        else:
            response_statement = "You don't have any private clouds."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetPrivateCloudsByOrganisationRequest(SingleRequest):
    ID = 11
    NAME = 'get_private_clouds_by_organisation'

    def __init__(self):
        super(GetPrivateCloudsByOrganisationRequest, self).__init__(
            method='GET',
            endpoint='openstack-tenants',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_organisations = extract_names(self.original)

        if len(extracted_organisations) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar = getSimilarNames(extracted_organisations, organisations)
            if most_similar == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + extracted_organisations[0] + "\". Please check that an " \
                                                                    "organisation with that name exists."
            else:

                self.parameters["customer"] = organisations_with_uuid[most_similar]
                response = self.send()

                clouds = [cloud["name"] for cloud in response]

                if len(clouds) > 1:
                    response_statement = \
                        "You have {n} private clouds in {similar}.\n" \
                        "They are:\n    {clouds}" \
                        .format(
                            n=len(clouds),
                            similar=most_similar,
                            clouds="\n    ".join(clouds)
                        )
                elif len(clouds) == 1:
                    response_statement = \
                        "You have 1 private cloud in {similar}.\n" \
                        "It's name is {cloud}." \
                        .format(
                            similar=most_similar,
                            cloud=clouds[0]
                        )
                else:
                    response_statement = "You don't have any private clouds in " + most_similar + ". "

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetPrivateCloudsByProjectAndOrganisationRequest(SingleRequest):
    ID = 16
    NAME = 'get_private_clouds_by_project_and_organisation'

    def __init__(self):
        super(GetPrivateCloudsByProjectAndOrganisationRequest, self).__init__(
            method='GET',
            endpoint='openstack-tenants',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_names = extract_names(self.original)
        project_name = extracted_names[:1]
        organisation_name = extracted_names[1:]

        if len(extracted_names) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's nor project's name in your request! " \
                                 "Please write it out in capital case!"
        elif len(organisation_name) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar_organisation = getSimilarNames(organisation_name, organisations)
            if most_similar_organisation == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + organisation_name[0] + "\". Please check that an " \
                                                              "organisation with that name exists."
            else:

                secondreq = GetProjectsAndIdsByOrganisationRequest()
                secondreq.token = self.token
                secondreq.parameters["customer"] = organisations_with_uuid[most_similar_organisation]
                projects_with_uuid = secondreq.process()
                projects = [x for x in projects_with_uuid]

                most_similar_project = getSimilarNames(project_name, projects)

                if most_similar_project == "":
                    response_statement = "Sorry, I wasn't able to find a project with the name \"" \
                                         + project_name[0] + "\". Please check that a " \
                                                             "project with that name exists."

                else:

                    self.parameters["project"] = projects_with_uuid[most_similar_project]
                    response = self.send()

                    clouds = [cloud["name"] for cloud in response]

                    if len(clouds) > 1:
                        response_statement = \
                            "You have {n} private clouds in project {similar_project} of organisation " \
                            "{similar_organisation}.\nThey are:\n    {clouds}" \
                            .format(
                                n=len(clouds),
                                similar_project=most_similar_project,
                                similar_organisation=most_similar_organisation,
                                clouds="\n    ".join(clouds)
                            )
                    elif len(clouds) == 1:
                        response_statement = \
                            "You have 1 private cloud in project {similar_project} of organisation " \
                            "{similar_organisation}.\nIt's name is {cloud}." \
                            .format(
                                similar_project=most_similar_project,
                                similar_organisation=most_similar_organisation,
                                cloud=clouds[0]
                            )
                    else:
                        response_statement = "You don't have any private clouds in project " + most_similar_project + \
                                             " of organisation " + most_similar_organisation + ". "

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetAuditLogByOrganisationRequest(SingleRequest):
    ID = 12
    NAME = 'get_audit_log_by_organisation'

    def __init__(self):
        super(GetAuditLogByOrganisationRequest, self).__init__(
            method='GET',
            endpoint='events',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_organisations = extract_names(self.original)

        if len(extracted_organisations) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar = getSimilarNames(extracted_organisations, organisations)
            if most_similar == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + extracted_organisations[0] + "\". Please check that an " \
                                                                    "organisation with that name exists."
            else:
                self.parameters["scope"] = "https://api.etais.ee/api/customers/" + str(
                    organisations_with_uuid[most_similar]) + "/"
                self.parameters["page_size"] = 10  # This param represents the last n events that will be displayed
                response = self.send()

                log_entries = []
                for entry in response:
                    date = dateutil.parser.parse(entry["@timestamp"]).astimezone().strftime('%Y-%m-%d %H:%M')
                    message = entry["message"]
                    user = (entry["user_full_name"] if "user_full_name" in entry else "")
                    eventtype = entry["event_type"]
                    log_entries.append("\n" + date + "\nEvent: " + eventtype + "\n" + message + (
                        "\nUser: " + user if "user_full_name" in entry else ""))

                if len(log_entries) > 1:
                    response_statement = "Here are the last " + str(
                        len(log_entries)) + " audit log entries in " + most_similar + ": "
                    response_statement += "\n".join(log_entries)
                elif len(log_entries) == 1:
                    response_statement = "You have 1 audit log entry in " + most_similar + ": "
                    response_statement += log_entries[0] + "."
                else:
                    response_statement = "Audit log in " + most_similar + " is empty. "

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetAuditLogByProjectAndOrganisationRequest(SingleRequest):
    ID = 13
    NAME = 'get_audit_log_by_project_and_organisation'

    def __init__(self):
        super(GetAuditLogByProjectAndOrganisationRequest, self).__init__(
            method='GET',
            endpoint='events',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_names = extract_names(self.original)
        project_name = extracted_names[:1]
        organisation_name = extracted_names[1:]

        if len(extracted_names) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's nor project's name in your request! " \
                                 "Please write it out in capital case!"
        elif len(organisation_name) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar_organisation = getSimilarNames(organisation_name, organisations)
            if most_similar_organisation == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + organisation_name[0] + "\". Please check that an " \
                                                              "organisation with that name exists."
            else:

                secondreq = GetProjectsAndIdsByOrganisationRequest()
                secondreq.token = self.token
                secondreq.parameters["customer"] = organisations_with_uuid[most_similar_organisation]
                projects_with_uuid = secondreq.process()
                projects = [x for x in projects_with_uuid]

                most_similar_project = getSimilarNames(project_name, projects)

                if most_similar_project == "":
                    response_statement = "Sorry, I wasn't able to find a project with the name \"" \
                                         + project_name[0] + "\". Please check that a " \
                                                             "project with that name exists."

                else:

                    self.parameters["scope"] = "https://api.etais.ee/api/projects/" + str(
                        projects_with_uuid[most_similar_project]) + "/"
                    self.parameters["page_size"] = 10  # This param represents the last n events that will be displayed
                    response = self.send()

                    log_entries = []
                    for entry in response:
                        date = dateutil.parser.parse(entry["@timestamp"]).astimezone().strftime('%Y-%m-%d %H:%M')
                        message = entry["message"]
                        user = (entry["user_full_name"] if "user_full_name" in entry else "")
                        eventtype = entry["event_type"]
                        log_entries.append("\n" + date + "\nEvent: " + eventtype + "\n" + message + (
                            "\nUser: " + user if "user_full_name" in entry else ""))

                    if len(log_entries) > 1:
                        response_statement = "Here are the last " + str(len(log_entries)) \
                                            + " audit log entries in project " + most_similar_project + \
                                            " of organisation " + most_similar_organisation + ": "
                        response_statement += "\n".join(log_entries)
                    elif len(log_entries) == 1:
                        response_statement = "You have 1 audit log entry in project " + most_similar_project + \
                                             " of organisation " + most_similar_organisation + ": "
                        response_statement += log_entries[0] + "."
                    else:
                        response_statement = "Audit log in project " + most_similar_project + " of organisation " + \
                                             most_similar_organisation + " is empty. "

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetTeamOfOrganisationRequest(SingleRequest):
    ID = 10
    NAME = 'get_team_of_organisation'

    def __init__(self):
        super(GetTeamOfOrganisationRequest, self).__init__(
            method='GET',
            endpoint='customers',
            parameters={
                "page_size": 100
            }
        )

    def process(self):

        firstreq = GetOrganisationsAndIdsRequest()
        firstreq.token = self.token

        organisations_with_uuid = firstreq.process()
        organisations = [x for x in organisations_with_uuid]

        extracted_organisations = extract_names(self.original)

        if len(extracted_organisations) == 0:
            response_statement = "Sorry, I wasn't able to find an organisation's name in your request! " \
                                 "Please write it out in capital case!"
        else:
            most_similar = getSimilarNames(extracted_organisations, organisations)
            if most_similar == "":
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + extracted_organisations[0] + "\". Please check that an " \
                                                                    "organisation with that name exists."
            else:

                self.endpoint += "/" + organisations_with_uuid[most_similar] + "/users/"
                response = self.send()

                print(response)
                owners = [owner['full_name'] for owner in response if owner["role"] == "owner" and
                          owner['full_name'] != ""]
                supportusers = [supportuser['full_name'] for supportuser in response if
                                supportuser["role"] == "support_user" and supportuser['full_name'] != ""]
                others = [other['full_name'] for other in response if other["role"] is None and
                          other['full_name'] != ""]

                response_statement = "The following people are team members of " + most_similar + ": "
                if len(owners) > 1:
                    response_statement += "\nOwners: " + (", ".join(owners)) + "."
                elif len(owners) == 1:
                    response_statement += "\nThe owner: " + str(owners[0]) + "."
                if len(supportusers) > 1:
                    response_statement = "\nSupport: " + (", ".join(owners)) + ". "
                elif len(supportusers) == 1:
                    response_statement += "\nThe support: " + str(supportusers[0]) + ". "
                elif len(others) > 1:
                    response_statement += "\nOthers: " + (", ".join(owners)) + "."
                elif len(others) == 1:
                    response_statement += "\nOther: " + str(others[0]) + "."
                if len(owners) + len(supportusers) == 0:
                    response_statement = "The organisation " + most_similar + " doesn't have any team members. "

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetTotalCostGraphRequest(SingleRequest):
    ID = 5
    NAME = 'get_totalcosts'
    HELP = ("---\n"
            "GET TOTAL COST GRAPH REQUEST\n"
            "I AM A WELL DEFINED HELP MESSAGE\n"
            "---")

    def __init__(self):
        super(GetTotalCostGraphRequest, self).__init__(
            method='GET',
            endpoint='invoices',
        )

    def process(self):
        response = self.send()

        data = response

        graphdata = {}

        num_to_month = {
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec'
        }

        plotx = []
        ploty = []

        lastmonths = 6

        if len(data) >= lastmonths:
            maxrange = lastmonths
        else:
            maxrange = len(data)

        for i in range(maxrange - 1, -1, -1):
            plotx.append(num_to_month[data[i]['month']] + " " + str(data[i]['year']))
            ploty.append(float(data[i]['total']))

        graphdata['x'] = plotx
        graphdata['y'] = ploty
        graphdata['graphID'] = 1

        return {
            'data': graphdata,
            'type': 'graph'
        }


class CreateVMRequest(InputRequest):
    ID = 7
    NAME = 'create_vm'

    def __init__(self):
        super(CreateVMRequest, self).__init__(
            [
                (
                    'continue',
                    QA('Do you wanna create a VM?',
                       check_answer=(lambda x, y: True if x.startswith("y") else None),
                       formatter="y/n"
                       )
                ),
                (
                    'name',
                    QA('Input name for vm.',
                       check_answer=(lambda x, y: x),
                       formatter=""
                       )
                ),
                (
                    'service_project_link',
                    QA('For which project?',
                       possible_answers=possible_projects,
                       check_answer=(lambda x, y: y[x] if x in y else None),
                       formatter=(lambda x: str(list(x)))
                       )
                ),
                (
                    'flavor',
                    QA('Which flavor to use?',
                       possible_answers=possible_flavors,
                       check_answer=(lambda x, y: y[x] if x in y else None),
                       formatter=(lambda x: str(list(x)))
                       )
                ),
                (
                    'image',
                    QA('Which image to use?',
                       possible_answers=possible_image,
                       check_answer=(lambda x, y: y[x] if x in y else None),
                       formatter=(lambda x: str(list(x)))
                       )
                ),
                (
                    'system_volume_size',
                    QA('System volume size in MB?',
                       possible_answers=possible_system_volume_size,
                       check_answer=(lambda x, y: x if int(x) >= y else None),
                       formatter=(lambda x: f"Must be more than {x}")
                       )
                ),
                (
                    'data_volume_size',
                    QA('Data volume size in MB?',
                       possible_answers=10240,
                       check_answer=(lambda x, y: x if int(x) >= y else None),
                       formatter=(lambda x: f"Must be more than {x}")
                       )
                ),
                (
                    'internal_ips_set',
                    QA('Which network to use?',
                       possible_answers=possible_networks,
                       check_answer=(lambda x, y: y[x] if x in y else None),
                       formatter=(lambda x: str(list(x)))
                       )
                ),
                (
                    'floating_ips',
                    QA('Add public ip?',
                       check_answer=(lambda x, y: x.startswith("y")),
                       formatter="y/n"
                       )
                ),
                (
                    'security_groups',
                    QA('Which security groups to use (comma separated)?',
                       possible_answers=possible_security_groups,
                       check_answer=(lambda x, y: [y[g.strip()] for g in x.strip(",").split(",") if g.strip() in y]),
                       formatter=(lambda x: str(list(x))))
                ),
                (
                    'ssh_public_key',
                    QA('Which key to use?',
                       possible_answers=possible_keys,
                       check_answer=(lambda x, y: y[x] if x in y else None),
                       formatter=(lambda x: str(list(x)))
                       )
                )
            ],
            bad_end_msg="Not creating vm."
        )

    def process(self):
        question = super(CreateVMRequest, self).process()

        log.debug(self.parameters)

        if question is not None:
            return text(question)

        # BELOW IS VM CREATION

        if self.parameters['floating_ips']:
            floating_ips = [{'subnet': self.parameters['internal_ips_set']}]
        else:
            floating_ips = []

        try:
            response = CreateVM(
                image=self.parameters['image'],
                internal_ips_set=[{'subnet': self.parameters['internal_ips_set']}],
                floating_ips=floating_ips,
                flavor=self.parameters['flavor'],
                service_project_link=self.parameters['service_project_link']['value'],
                ssh_public_key=self.parameters['ssh_public_key'],
                name=self.parameters['name'],
                security_groups=[{
                    'url': sg['value']
                } for sg in self.parameters['security_groups']],
                system_volume_size=int(self.parameters['system_volume_size']),
                data_volume_size=int(self.parameters['data_volume_size'])
            ).set_token(self.token).process()
            log.info(response)
            return text(response['state'])
        except Exception as e:
            log.exception(e)
            return text("Couldn't create vm")


def possible_projects(token, parameters):
    return GetPossibleProjects().set_token(token).process()


def possible_flavors(token, parameters):
    return GetPossibleFlavors(parameters['service_project_link']['settings_uuid']).set_token(token).process()


def possible_image(token, parameters):
    return GetPossibleImages(parameters['service_project_link']['settings_uuid']).set_token(token).process()


def possible_system_volume_size(token, parameters):
    return GetSystemVolumeSize(parameters['image'].strip("/").split("/")[-1]).set_token(token).process()


def possible_networks(token, parameters):
    return GetPossibleNetworks(parameters['service_project_link']['settings_uuid']).set_token(token).process()


def possible_security_groups(token, parameters):
    return GetSecurityGroups(parameters['service_project_link']['settings_uuid']).set_token(token).process()


def possible_keys(token, parameters):
    return GetPossibleKeys().set_token(token).process()


class GetHelpRequest(SingleRequest):
    ID = None  # todo in future, if help has parameters, give help an ID so that you can see the help for help
    NAME = 'get_help'

    def __init__(self):
        super(GetHelpRequest, self).__init__(
            endpoint='please stop lollygagging'
        )

    def process(self):

        subclasses = all_subclasses()

        response_statement = ""

        for request in subclasses:
            if request.ID is not None:
                helpmsg = request.HELP
                if request.HELP is None:
                    helpmsg = request.NAME + " does not have HELP defined"
                response_statement += helpmsg + "\n"

        return {
            'data': response_statement,
            'type': 'text'
        }


# --------------------- REQUESTS FOR INTERNAL USE ---------------------


class GetPossibleImages(SingleRequest):
    def __init__(self, settings_uuid):
        super().__init__(
            'GET',
            'openstacktenant-images',
            parameters={
                'settings_uuid': settings_uuid
            }
        )

    def process(self):
        return {image['name']: image['url'] for image in self.send()}


class GetPossibleFlavors(SingleRequest):
    def __init__(self, settings_uuid):
        super().__init__(
            'GET',
            'openstacktenant-flavors',
            parameters={
                'settings_uuid': settings_uuid
            }
        )

    def process(self):
        return {flavor['name']: flavor['url'] for flavor in self.send()}


class GetPossibleKeys(SingleRequest):
    def __init__(self):
        super().__init__(
            'GET',
            'keys'
        )

    def process(self):
        return {key['name']: key['url'] for key in self.send()}


class GetPossibleNetworks(SingleRequest):
    def __init__(self, settings_uuid):
        super().__init__(
            'GET',
            'openstacktenant-subnets',
            parameters={
                'settings_uuid': settings_uuid
            }
        )

    def process(self):
        return {network['name']: network['url'] for network in self.send()}


class GetSecurityGroups(SingleRequest):
    def __init__(self, settings_uuid):
        super().__init__(
            'GET',
            'openstacktenant-security-groups',
            parameters={
                'settings_uuid': settings_uuid
            }
        )

    def process(self):
        return {group['name']: {'value': group['url']} for group in self.send()}


class GetPossibleProjects(SingleRequest):
    def __init__(self):
        super().__init__(
            'GET',
            'openstacktenant-service-project-link'
        )

    def process(self):
        return {
            project['project_name']: {
                'value': project['url'],
                'settings_uuid': GetSetting(project['service_uuid']).set_token(self.token).process()
            } for project in self.send()
        }


class GetSetting(SingleRequest):
    def __init__(self, service_uuid):
        super().__init__(
            'GET',
            'openstacktenant/{}/'.format(service_uuid)
        )

    def process(self):
        return self.send()['settings_uuid']


class GetSystemVolumeSize(SingleRequest):
    def __init__(self, image):
        super().__init__(
            'GET',
            'openstacktenant-images/{}/'.format(image)
        )

    def process(self):
        return self.send()['min_disk']


class CreateVM(SingleRequest):
    def __init__(self, data_volume_size, flavor, floating_ips, image, internal_ips_set, name, security_groups,
                 service_project_link, ssh_public_key, system_volume_size):
        super().__init__(
            'POST',
            'openstacktenant-instances',
            parameters=[],
            data=dict(
                data_volume_size=data_volume_size,
                flavor=flavor,
                floating_ips=floating_ips,
                image=image,
                internal_ips_set=internal_ips_set,
                name=name,
                security_groups=security_groups,
                service_project_link=service_project_link,
                ssh_public_key=ssh_public_key,
                system_volume_size=system_volume_size
            )
        )

    def process(self):
        response = self.send()
        log.debug(response)
        return response


class GetOrganisationsAndIdsRequest(SingleRequest):
    NAME = 'util_get_organisations'

    def __init__(self):
        super(GetOrganisationsAndIdsRequest, self).__init__(
            method='GET',
            endpoint='customers'
        )

    def process(self):
        response = self.send()

        return {organisation['name']: organisation["uuid"] for organisation in response}


class GetProjectsAndIdsByOrganisationRequest(SingleRequest):
    NAME = 'util_get_projects_by_organisation'

    def __init__(self):
        super(GetProjectsAndIdsByOrganisationRequest, self).__init__(
            method='GET',
            endpoint='projects',
            parameters={}
        )

    def process(self):
        response = self.send()

        return {project['name']: project["uuid"] for project in response}


def all_subclasses(cls=Request):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]

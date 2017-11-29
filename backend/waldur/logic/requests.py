import itertools
from collections import OrderedDict
from logging import getLogger

from common.request import WaldurConnection, InvalidTokenError
from waldur.nameparser import extract_names, getSimilarNames

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

    def request(self, method, endpoint, parameters):
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
            data=parameters
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
                 parameters=None
                 ):
        super(SingleRequest, self).__init__()

        if endpoint is None:
            raise ValueError("Endpoint must be set for request")

        if method is None:
            method = 'GET'

        if parameters is None:
            parameters = {}

        self.endpoint = endpoint
        self.method = method
        self.parameters = parameters

    def send(self):
        return super(SingleRequest, self).request(
            method=self.method,
            endpoint=self.endpoint,
            parameters=self.parameters
        )

    def process(self):
        raise NotImplementedError("Subclass must override this method")


class QA(object):
    def __init__(self, question, possible_answers, *args):
        self.question = question.format(possible_answers, args)
        self.possible_answers = possible_answers
        self.waiting_for_answer = True

        self.answer = None

    def check_answer(self, i):
        # check if answer is good
        if i in self.possible_answers:
            self.answer = i
            self.waiting_for_answer = False
            return True

        return False

    def get_answer(self):
        if self.answer is None:
            raise Exception("Answer should not be None at this point")
        return self.answer


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
        self._next_question()

    def set_input(self, data):
        """
        Method to give input to Request object
        """
        self.input = data
        return self

    def get_input(self):
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
            self._evaluate()
            return type(self).process(self)
        else:
            return self.bad_end_msg

    def _evaluate(self):
        """
        Replaces QA objects in questions dict with answers from QA objects.
        Ex. {'os': QA_OBJECT} -> {'os': 'debian'}
        """
        for q in self.questions:
            self.parameters[q] = self.questions[q].get_answer()

        if self.parameters is None:
            raise Exception("parameters should not be None at this point")

    def process(self):
        # bot needs token to know who to query
        self.check_token()
        if self.waiting_for_input:
            return self.handle_question()

        return None

    def handle_question(self):
        """
        Handles current question, if waiting for answer -> asks, else continues to next question
        :return: message to client
        """
        i = self.get_input()

        if self.current is None:
            return self._end(True)

        question = self.questions[self.current]

        if question.waiting_for_answer:
            if i is not None:
                if question.check_answer(i):
                    self._next_question()
                    return self.handle_question()
                else:
                    return self._end(False)
            else:
                return question.question
        else:
            raise Exception("Should be at the next question at this point")


class GetServicesRequest(SingleRequest):
    ID = 1
    NAME = 'get_services'

    def __init__(self):
        super(GetServicesRequest, self).__init__(
            method='GET',
            endpoint='projects',
        )

    def process(self):
        response = self.send()

        services = set([service['name'] for services in response for service in services["services"]])

        if len(services) >= 1:
            response_statement = \
                "Your organisation is using {n} services. " \
                "They are {services}." \
                .format(
                    n=len(services),
                    services=", ".join(services)
                )
        elif len(services) == 1:
            response_statement = \
                "Your organization is using 1 service. " \
                "This service is {service}." \
                .format(
                    service=services[0]
                )
        else:
            response_statement = "Your organisation isn't using any services."

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


class GetVmsRequest(SingleRequest):
    ID = 3
    NAME = 'get_vms'

    def __init__(self):
        super(GetVmsRequest, self).__init__(
            method='GET',
            endpoint='openstacktenant-instances',
        )

    def process(self):
        response = self.send()

        len_all = 0
        statement = ""
        organisations = itertools.groupby(response, lambda vm: vm['customer_name'])
        for organisation, vms in organisations:
            names = {vm['name'] + ": " + ("None" if len(vm['external_ips']) == 0 else ", ".join(vm['external_ips'])) for vm in vms}
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


class GetOrganisationsRequest(SingleRequest):
    ID = 4
    NAME = 'get_organisations'

    def __init__(self):
        super(GetOrganisationsRequest, self).__init__(
            method='GET',
            endpoint='customers'
        )

    def process(self):
        response = self.send()

        organisations = [organisation['name'] for organisation in response]

        if len(organisations) > 1:
            response_statement = \
                "You are part of {n} organisations. " \
                "They are {organisations}" \
                .format(
                    n=len(organisations),
                    organisations=", ".join(organisations)
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


class GetServicesByOrganisationRequest(SingleRequest):
    ID = 6
    NAME = 'get_services_by_organisation'

    def __init__(self):
        super(GetServicesByOrganisationRequest, self).__init__(
            method='GET',
            endpoint='projects',
            parameters={}
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

                service_names = set([service['name'] for services in response for service in services["services"]])

                if len(service_names) > 1:
                    response_statement = "You have " + str(
                        len(service_names)) + " services in use in " + most_similar + ". "
                    response_statement += "They are " + (", ".join(service_names)) + ". "
                elif len(service_names) == 1:
                    response_statement = "You have 1 service in use in " + most_similar + ". "
                    response_statement += "The service is " + str(service_names[0])
                else:
                    response_statement = "You don't have any services in use in " + most_similar + ". "

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
            parameters={}
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

                vm_names = {vm['name']: (["None"] if len(vm['external_ips']) == 0 else vm['external_ips']) for vm in
                            response}

                if len(vm_names) > 1:
                    response_statement = "You have " + str(len(vm_names)) + " virtual machines in " + most_similar + ". "
                    response_statement += "Here are their names and public IPs: "
                    response_statement += "; ".join(
                        [vm + ": " + (", ".join(vm_names[vm])) for vm in vm_names.keys()]) + ". "
                elif len(vm_names) == 1:
                    response_statement = "You have 1 virtual machine in " + most_similar + ". "
                    response_statement += "The virtual machine is " + str(list(vm_names.keys())[0])
                    response_statement += " and it's public IP: " + str(", ".join(list(vm_names.values())[0])) + ". "
                else:
                    response_statement = "You don't have any virtual machines in " + most_similar + ". "

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
            endpoint='customers'
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

                self.endpoint += "/" + organisations_with_uuid[most_similar]
                response = self.send()

                owners = [owner['full_name'] for owner in response["owners"]]
                supportusers = [supportuser['full_name'] for supportuser in response["support_users"]]

                response_statement = "The following people are team members of " + most_similar + ": "
                if len(owners) > 1:
                    response_statement += "\nOwners: " + (", ".join(owners)) + "."
                elif len(owners) == 1:
                    response_statement += "\nThe owner: " + str(owners[0]) + "."
                if len(supportusers) > 1:
                    response_statement = "\nSupport: " + (", ".join(owners)) + ". "
                elif len(supportusers) == 1:
                    response_statement += "\nThe support: " + str(supportusers[0]) + ". "
                if len(owners) + len(supportusers) == 0:
                    response_statement = "The organisation " + most_similar + " doesn't have any team members. "

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
        )

    def process(self):
        response = self.send()

        clouds = [cloud['name'] for cloud in response]

        if len(clouds) >= 1:
            response_statement = \
                "You have {n} private clouds. " \
                "They are {clouds}." \
                .format(
                    n=len(clouds),
                    clouds=", ".join(clouds)
                )
        elif len(clouds) == 1:
            response_statement = \
                "You have 1 private cloud. " \
                "It's name is {cloud}." \
                .format(
                    cloud=clouds[0]
                )
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
            parameters={}
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
                    response_statement = "You have " + str(len(clouds)) + " private clouds in " + most_similar + ". "
                    response_statement += "Here are their names: "
                    response_statement += ", ".join(clouds) + ". "
                elif len(clouds) == 1:
                    response_statement = "You have 1 private cloud in " + most_similar + ". "
                    response_statement += "The cloud is " + clouds[0] + "."
                else:
                    response_statement = "You don't have any private clouds in " + most_similar + ". "

        return {
            'data': response_statement,
            'type': 'text'
        }

class GetTotalCostGraphRequest(SingleRequest):
    ID = 5
    NAME = 'get_totalcosts'

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

    POSSIBLE_OS = ['centos7', 'debian']  # todo query waldur for possible os'es

    CONFIRM = 'Do you wanna create a VM? {}'
    ASK_OS = 'Which os to use? {}'
    ASK_IP = 'Add public ip? {}'
    EXIT = 'Not creating VM'

    def __init__(self):
        super(CreateVMRequest, self).__init__(
            [
                (
                    'continue',
                    QA(self.CONFIRM, ['y'])
                ),
                (
                    'os',
                    QA(self.ASK_OS, self.POSSIBLE_OS)
                ),
            ],
            bad_end_msg=self.EXIT
        )

    def process(self):
        question = super(CreateVMRequest, self).process()

        if question is not None:
            return text(question)

        return text("This is the part where the vm is created, todo")


class GetHelpRequest(SingleRequest):
    ID = 11
    NAME = 'get_help'

    def __init__(self):
        super(GetHelpRequest, self).__init__(
            endpoint='git gud'
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

class GetOrganisationsAndIdsRequest(SingleRequest):
    ID = 99
    NAME = 'util_get_organisations'

    def __init__(self):
        super(GetOrganisationsAndIdsRequest, self).__init__(
            method='GET',
            endpoint='customers'
        )

    def process(self):
        response = self.send()

        return {organisation['name']: organisation["uuid"] for organisation in response}


def all_subclasses(cls=Request):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]
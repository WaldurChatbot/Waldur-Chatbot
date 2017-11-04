from common.request import WaldurConnection, InvalidTokenException
from logging import getLogger

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
    ID = None
    NAME = None
    """
    Base class for Requests to Waldur API, should not be instantiated directly.
    Subclass must override process() and if needed set_original()
    Subclasses must also have NAME and ID variables.
    """

    def __init__(self,
                 method=None,
                 endpoint=None,
                 parameters=None
                 ):

        if endpoint is None:
            raise ValueError("Endpoint must be set for request")

        if method is None:
            method = 'GET'

        if parameters is None:
            parameters = {}

        self.need_values = []
        for key, value in parameters.items():
            if value is None:
                self.need_values.append(key)

        self.endpoint = endpoint
        self.method = method
        self.parameters = parameters

        self.waiting_for_input = False
        self.input = None

        self.token = None
        self.original = None
        self.sep = sep

    def set_token(self, token):
        """
        :param token: Waldur API authentication token
        """
        self.token = token
        return self  # builder pattern yo

    def set_original(self, query):
        """
        Meant for requests that may need info from the original statement sent to backend.
        Subclass that needs original statement must override this method.
        :param query: original query sent to backend
        """
        self.original = query
        return self

    def request(self):
        """
        Method to query Waldur API.
        :return: response from Waldur API
        """
        # todo figure out how to get this programmatically
        api_url = "https://api.etais.ee/api/"

        if self.token is None:
            raise InvalidTokenException("Token is missing")

        waldur = WaldurConnection(
            api_url=api_url,
            token=self.token
        )

        response = waldur.query(
            method=self.method,
            endpoint=self.endpoint,
            data=self.parameters
        )

        return response

    def process(self):
        """
        Processes the Request, i.e. calls request() and formats the response.
        :return: Dict or tuple of dicts with 2 keys: 'type' and 'data'
                    'type' values:  'text' if data is string
                                    'graph' if data is dict from which a graph can be constructed
                                    'prompt' if data is a string question for which we expect an answer from client
                 May return more than 1 dict as a tuple, in which case all dicts are processed sequentially by clienta
        """
        raise NotImplementedError("Subclass must override this method")

    def set_input(self, data):
        """
        Method to give input to Request object
        """
        self.input = data

    def get_input(self):
        """
        Method to get input, input is set back to None after call
        :return: string input
        """
        if self.input is None:
            raise Exception("No input")  # todo custom exception
        else:
            out = self.input.strip()
            self.input = None
            return out

    def to_string(self):  # todo do we need this?
        return "REQUEST" + self.sep + type(self).NAME

    @staticmethod
    def from_string(string):
        """
        Converts request from string to matching Request object
        :param string: request as string, ex. 'REQUEST~get_projects'
        :return: Matching Request object
        """
        tokens = string.strip(sep).split(sep)

        request_name = tokens[1]

        # todo cant this be done in a better, more automatic way?
        if request_name == GetServicesRequest.NAME:
            return GetServicesRequest()
        if request_name == GetProjectsRequest.NAME:
            return GetProjectsRequest()
        if request_name == GetVmsRequest.NAME:
            return GetVmsRequest()
        if request_name == GetOrganisationsRequest.NAME:
            return GetOrganisationsRequest()
        if request_name == GetTotalCostGraphRequest.NAME:
            return GetTotalCostGraphRequest()
        if request_name == CreateVMRequest.NAME:
            return CreateVMRequest()

        raise Exception("Unknown request")


class GetServicesRequest(Request):
    ID = 1
    NAME = 'get_services'

    def __init__(self):
        super(GetServicesRequest, self).__init__(
            method='GET',
            endpoint='projects',
        )

    def process(self):
        response = self.request()

        services = response[0]['services']

        names = [service['name'] for service in services]

        if len(names) >= 1:
            response_statement = "Your organisation is using " + str(len(names)) + " services. "
            response_statement += "They are " + (", ".join(names))
        elif len(names) == 1:
            response_statement = "Your organisation is using 1 service. "
            response_statement += "This service is " + str(names[0])
        else:
            response_statement = "Your organisation isn't using any services."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetProjectsRequest(Request):
    ID = 2
    NAME = 'get_projects'

    def __init__(self):
        super(GetProjectsRequest, self).__init__(
            method='GET',
            endpoint='customers',
        )

    def process(self):
        response = self.request()

        # todo take all organization, not only the first
        projects = response[0]['projects']

        names = [project['name'] for project in projects]

        if len(names) > 1:
            response_statement = "You have " + str(len(names)) + " projects. "
            response_statement += "They are " + (", ".join(names))
        elif len(names) == 1:
            response_statement = "You have 1 project. "
            response_statement += "The project is " + str(names[0])
        else:
            response_statement = "You don't have any projects."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetVmsRequest(Request):
    ID = 3
    NAME = 'get_vms'

    def __init__(self):
        super(GetVmsRequest, self).__init__(
            method='GET',
            endpoint='openstacktenant-instances',
        )

    def process(self):
        response = self.request()

        names = {vm['name']: vm['external_ips'] for vm in response}

        if len(names) > 1:
            response_statement = "You have " + str(len(names)) + " virtual machines. "
            response_statement += "Here are their names and public IPs " + "; ".join([ vm + ": " + (", ".join(names[vm])) for vm in names.keys()])
        elif len(names) == 1:
            response_statement = "You have 1 virtual machine. "
            response_statement += "The virtual machine is " + str(list(names.keys())[0])
            response_statement += " It's public IP is " + str(list(names.items())[0])
        else:
            response_statement = "You don't have any virtual machines."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetOrganisationsRequest(Request):
    ID = 4
    NAME = 'get_organisations'

    def __init__(self):
        super(GetOrganisationsRequest, self).__init__(
            method='GET',
            endpoint='customers'
        )

    def process(self):
        response = self.request()

        names = [organisation['name'] for organisation in response]

        if len(names) > 1:
            response_statement = "You are part of " + str(len(names)) + " organisations. "
            response_statement += "They are " + (", ".join(names))
        elif len(names) == 1:
            response_statement = "You are part of 1 organisation. "
            response_statement += "The organisation is " + str(names[0])
        else:
            response_statement = "You you aren't part of any organisation."

        return {
            'data': response_statement,
            'type': 'text'
        }


class GetTotalCostGraphRequest(Request):
    ID = 5
    NAME = 'get_totalcosts'

    def __init__(self):
        super(GetTotalCostGraphRequest, self).__init__(
            method='GET',
            endpoint='invoices',
        )

    def process(self):
        response = self.request()

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

        for i in range(maxrange-1, -1, -1):
            plotx.append(num_to_month[data[i]['month']] + " " + str(data[i]['year']))
            ploty.append(float(data[i]['total']))

        graphdata['x'] = plotx
        graphdata['y'] = ploty
        graphdata['graphID'] = 1

        return {
            'data': graphdata,
            'type': 'graph'
        }


class CreateVMRequest(Request):
    ID = 6
    NAME = 'create_vm'

    POSSIBLE_OS = ['centos7', 'debian']  # todo query waldur for possible os'es

    CONFIRM = text('Do you wanna create a VM? [y/n]')
    ASK_OS  = text('Which os to use? {}')
    ASK_IP  = text('Add public ip? [y/n]')
    EXIT = text('Not creating VM')

    def __init__(self):
        super(CreateVMRequest, self).__init__(
            method='todo',
            endpoint='todo',  # todo
        )
        self.state = 0

        self.os = None
        self.public_ip = None
        self.cloud = None
        self.project = None
        self.ram = None
        self.cores = None
        self.disk = None

        self.output = None

    def process(self):
        self.waiting_for_input = True
        print(self.state)

        if self.state < 2:  # make sure the user wants vm
            self.handle_confirm()
        elif self.state < 4:  # ask for os
            self.handle_os()
        elif self.state < 6:  # ask for os
            self.handle_ip()

        print(self.output)
        return self.output

    def end(self):
        self.waiting_for_input = False
        self.output = self.EXIT

    def handle_confirm(self):
        if self.state == 0:
            self.output = self.CONFIRM
            self.state = 1
        elif self.state == 1:
            if self.expect(['y', 'yes']):
                self.state = 2
                self.handle_os()
            else:
                self.end()
        else:
            raise Exception("Bad state {} for handle_confirm".format(self.state))

    def handle_os(self):
        if self.state == 2:
            self.output = self.ASK_OS['data'].format(self.POSSIBLE_OS)
            self.state = 3
        elif self.state == 3:
            if self.expect(self.POSSIBLE_OS):
                self.state = 4
                self.handle_ip()
            else:
                self.end()
        else:
            raise Exception("Bad state {} for handle_os".format(self.state))

    def handle_ip(self):
        if self.state == 4:
            self.output = self.ASK_IP
            self.state = 5
        elif self.state == 5:
            if self.expect(['y', 'yes']):
                self.state = 6
                self.end()  # todo continue
            else:
                self.end()
        else:
            raise Exception("Bad state {} for handle_ip".format(self.state))

    def expect(self, expected):
        return self.get_input() in expected

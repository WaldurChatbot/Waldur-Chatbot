from common.request import WaldurConnection, InvalidTokenException
from common.nameparser import extract_names, getSimilarNames
from logging import getLogger

log = getLogger(__name__)

# separator for string format
sep = "~"


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
        :return: Human readable response from Waldur API
        """
        raise NotImplementedError("Subclass must override this method")

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
        if request_name == GetProjectsByOrganisationRequest.NAME:
            return GetProjectsByOrganisationRequest()

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

class GetProjectsByOrganisationRequest(Request):
    ID = 6
    NAME = 'get_projects_by_organisation'

    def __init__(self):
        super(GetProjectsByOrganisationRequest, self).__init__(
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
                                 "Please write it out clearly!"
        else:
            most_similar = getSimilarNames(extracted_organisations, organisations)
            if (most_similar == ""):
                response_statement = "Sorry, I wasn't able to find an organisation with the name \"" \
                                     + extracted_organisations[0] + "\". Please check that an " \
                                                                    "organisation with that name exists."
            else:

                self.parameters["customer"] = organisations_with_uuid[most_similar]
                response = self.request()

                project_names = [project['name'] for project in response]

                if len(project_names) > 1:
                    response_statement = "You have " + str(len(project_names)) + " projects in " + most_similar + ". "
                    response_statement += "They are " + (", ".join(project_names)) + ". "
                elif len(project_names) == 1:
                    response_statement = "You have 1 project in " + most_similar + ". "
                    response_statement += "The project is " + str(project_names[0])
                else:
                    response_statement = "You don't have any projects in " + most_similar + ". "

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


# --------------------- REQUESTS FOR INTERNAL USE ---------------------

class GetOrganisationsAndIdsRequest(Request):
    ID = 99
    NAME = 'util_get_organisations'

    def __init__(self):
        super(GetOrganisationsAndIdsRequest, self).__init__(
            method='GET',
            endpoint='customers'
        )

    def process(self):
        response = self.request()

        return {organisation['name']:organisation["uuid"] for organisation in response}
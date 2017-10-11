from requests import Session, Request
import json
from .requestlogicadapter import RequestLogicAdapter
from chatterbot.conversation.statement import Statement


class GetOrganisationLogicAdapter(RequestLogicAdapter):
    def __init__(self):
        super(GetOrganisationLogicAdapter, self).__init__(
            endpoint='customers',
            method='GET',
            parameters={},
            optional_parameters={},
            auth=True,
            allowed=['all']
        )

    def can_process(self, statement):
        print("Processing? " + str(statement))
        words = ['my', 'projects']
        return all(x in statement.text.split() for x in words)

    def process(self, statement):
        print("Processing " + str(statement))
        token = "<changeme>"

        request = Request(
            self.method,
            "https://api.etais.ee/api/" + self.endpoint + "/",
            data=json.dumps(self.parameters)
        )

        session = Session()

        prepped = request.prepare()
        prepped.headers['Content-Type'] = 'application/json'
        prepped.headers['Authorization'] = 'token ' + token
        response = session.send(prepped)

        response_json = response.json()

        projects = response_json[0]['projects']

        names = []
        for project in projects:
            names.append(project['name'])

        print("Yo, u have " + str(len(names)) + " projects")
        print("They are " + str(names))

        print(json.dumps(response_json, indent=2))

        if response.status_code == 200:
            return Statement(response_json)
        else:
            raise Exception(response_json['message'])

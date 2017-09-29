
from requests import Session, Request
import json
import configparser

config = configparser.ConfigParser()
config.read('../configuration.ini')
backend = config['backend']
backend_url = backend['url'] + ':' + backend['port']

session = Session()


def query(q):
    request = Request(
        'POST',
        backend_url,
        data=json.dumps({'query': q})
    )

    prepped = request.prepare()
    prepped.headers['Content-Type'] = 'application/json'
    response = session.send(prepped)

    response_json = response.json()

    if response_json['status'] == 'ok':
        return response_json
    else:
        raise Exception(response_json['message'])

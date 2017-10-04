
from requests import Session, Request
import json
import configparser
import logging

config = configparser.ConfigParser()
config.read('../configuration.ini')
backend = config['backend']
backend_url = backend['url'] + ':' + backend['port']

logger = logging.getLogger(__name__)

session = Session()


def query(q):
    request = Request(
        'POST',
        backend_url,
        data=json.dumps({'query': q})
    )

    prepped = request.prepare()
    prepped.headers['Content-Type'] = 'application/json'
    logger.info("Sending request: " + str(request.data))
    response = session.send(prepped)

    response_json = response.json()

    if response_json['status'] == 'ok':
        logger.info("Received response: " + response_json['message'])
        return response_json
    else:
        logger.error("Received error response: " + response_json['message'])
        raise Exception(response_json['message'])

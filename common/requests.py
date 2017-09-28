
import requests as r
import json
import configparser

config = configparser.ConfigParser()
config.read('../configuration.ini')
backend_url = 'http://localhost:' + config['backend']['port']


def query(q):
    response = r.request(
            "POST",
            backend_url,
            data={'query': q}
    ).text
    response = json.loads(response)

    if 'message' in response:
        response = response['message']
    else:
        response = "Something went wrong, sorry!"
        try:
            print(response['error'])
        except Exception:
            pass

    return response

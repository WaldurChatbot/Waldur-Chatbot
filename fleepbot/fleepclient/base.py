"""Python Library for Fleep HTTP API.
"""

import requests
import json
import logging
import pprint

DEFAULT_API_VERSION = 2

class FleepApiBase(object):
    """Base class for HTTP API's
    """
    def __init__(self, base_url):
        """Initiates session
        """
        self.base_url = base_url.rstrip('/')  #: URL of web server providing API
        self.ws = requests.Session()
        self.code = None        #: result code of latest request
        self.expect = 200       #: if set expect this code from service and raise error if
        #: something else comes
        self.ticket = None
        self.requests = set()   #: requests processed by server
        self.api_version = DEFAULT_API_VERSION

    def _webapi_call(self, function, *args, **kwargs):
        logging.debug('-' * 60)

        url = '/'.join((self.base_url, function) + args)
        hdr = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'Keep-Alive'}
        if self.ticket:
            kwargs['ticket'] = self.ticket
            kwargs['api_version'] = self.api_version
        js = json.dumps(kwargs)

        logging.debug('REQUEST: %s', url)
        logging.debug("PARAMS: %s", js)

        r = self.ws.post(url, data = js, headers = hdr, verify = True)
        if r.text and r.text[0] in ('{', '['):
            res = json.loads(r.text)
        else:
            res = {}
        logging.debug('STATUS_CODE %s', r.status_code)
        logging.debug("RESULT:\n%s", pprint.pformat(res, 4))

        if self.expect is not None and r.status_code != self.expect:
            raise Exception("%s: Expect %d, got: %d %s" % (url, self.expect, r.status_code, r.raw.reason))

        self.code = r.status_code
        return res

    def _file_call(self, function, **kwargs):
        url = self.base_url + '/' + function
        files = kwargs.get('files')
        if files:
            del kwargs['files']
        logging.debug('REQUEST: %s', url)

        r = self.ws.post(url, params = {'ticket' : self.ticket}, files = files, verify = True)
        if r.text and r.text[0] in ('{', '['):
            res = json.loads(r.text)
        else:
            res = {}
        logging.debug('STATUS_CODE %s', r.status_code)
        logging.debug("RESULT:\n%s", pprint.pformat(res, 4))

        if self.expect is not None and r.status_code != self.expect:
            raise Exception("%s: Expect %d, got: %d %s" % (url, self.expect, r.status_code, r.raw.reason))

        self.code = r.status_code
        return res

    def get_token(self):
        """Get session token
        """
        return self.ws.cookies.get('token_id')

    def get_ticket(self):
        """Get ticket
        """
        return self.ticket

    def set_token(self, token = None, ticket = None):
        """Set session token
        """
        if token is not None:
            self.ws.cookies.set('token_id', token)
        if ticket is not None:
            self.ticket = ticket

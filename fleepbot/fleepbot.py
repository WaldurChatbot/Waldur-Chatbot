# Derived from https://github.com/fleephub/fleep-api/blob/master/python-client/chatbot.py

import uuid
import base64
import time

import logging, logging.config, logging.handlers
from configparser import ConfigParser

from fleepclient.cache import FleepCache
from fleepclient.utils import convert_xml_to_text
from common import request

import sys
sys.path.insert(0, '../')

logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)

log = logging.getLogger("Fleep")


def uuid_decode(b64uuid):
    ub = base64.urlsafe_b64decode(b64uuid + '==')
    uobj = uuid.UUID(bytes=ub)
    return str(uobj)


def process_msg(chat, msg):
    if msg.mk_message_type == 'text':
        txt = convert_xml_to_text(msg.message).strip()
        #print("got msg: %r" % msg.__dict__)
        log.info("got msg: %r" % msg.__dict__)
        chat.mark_read(msg.message_nr)
        #print('text: %s' % txt)
        log.info('text: %s' % txt)
        if txt[:1] == "!":
            chat.message_send(str(query(txt[1:])))


def query(input):
    #print("Query:    " + input)
    #logger.info("Query:    " + input)
    response = request.query(input)
    #print("Response: " + response)
    #logger.info(("Response: " + response))
    return response['message']


def main():
    config = ConfigParser()
    config.read('../configuration.ini')
    config = config['fleep']
    username = config['user']
    password = config['pass']
    server   = config['server']
    chatid   = config['chatid']

    #print('Login')
    log.info('Login')
    fc = FleepCache(server, username, password)
    #print('Loading contacts')
    #print('convs: %d' % len(fc.conversations))
    log.info('Loading contacts')
    log.info('convs: %d' % len(fc.conversations))

    chat_id = uuid_decode(chatid)
    chat = fc.conversations[chat_id]
    #print('chat_id: %s' % chat_id)
    log.info('chat_id: %s' % chat_id)

    chat_msg_nr = chat.read_message_nr

    while True:
        while True:
            msg = chat.get_next_message(chat_msg_nr)
            if not msg:
                break
            process_msg(chat, msg)
            chat_msg_nr = msg.message_nr

        if not fc.poll():
            time.sleep(1)
            continue


if __name__ == '__main__':
    main()

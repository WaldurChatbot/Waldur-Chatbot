# Derived from https://github.com/fleephub/fleep-api/blob/master/python-client/chatbot.py

import sys
sys.path.insert(0, '../')  # important for common import
from common import request

import uuid
import base64
import time
import logging, logging.config, logging.handlers
from configparser import ConfigParser
from fleepclient.cache import FleepCache
from fleepclient.utils import convert_xml_to_text

logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)
log = logging.getLogger("Fleep")


def uuid_decode(b64uuid):
    ub = base64.urlsafe_b64decode(b64uuid + '==')
    uobj = uuid.UUID(bytes=ub)
    return str(uobj)


def process_msg(chat, msg):
    if msg.mk_message_type == 'text':
        txt = convert_xml_to_text(msg.message).strip()
        log.debug("got msg: %r" % msg.__dict__)
        chat.mark_read(msg.message_nr)
        log.debug('text: %s' % txt)
        if txt[:1] == "!":
            chat.message_send(str(query(txt[1:])))


def query(input):
    log.info("IN:  " + input)
    response = request.query(input)
    log.info("OUT: " + response['message'])
    return response['message']


def main():
    log.info("Initializing bot")
    config = ConfigParser()
    config.read('../configuration.ini')
    fleep = config['fleep']
    username = fleep['user']
    password = fleep['pass']
    server   = fleep['server']
    chatid   = fleep['chatid']

    log.info('Login')
    fc = FleepCache(server, username, password)
    log.info('Loading contacts')
    log.info('convs: %d' % len(fc.conversations))

    chat_id = uuid_decode(chatid)
    chat = fc.conversations[chat_id]
    log.info('chat_id: %s' % chat_id)

    chat_msg_nr = chat.read_message_nr

    log.info("Bot initialized")
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

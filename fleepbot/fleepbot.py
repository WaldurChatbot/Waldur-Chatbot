# Derived from https://github.com/fleephub/fleep-api/blob/master/python-client/chatbot.py

import uuid
import base64
import time
import requests as r

from fleepclient.cache import FleepCache
from fleepclient.utils import convert_xml_to_text

backend_url = "http://localhost:4567/"

SERVER = 'https://fleep.io'
# how to identify chat
CHAT_CID = 'G0xzIA-BQq2iiADMqjZuZA'
CHAT_TOPIC = "Api send test"


def load_config():
    with open(".config") as config:
        return config.readline().strip(), config.readline().strip()


def find_chat_by_topic(fc, topic):
    for conv_id in fc.conversations:
        conv = fc.conversations[conv_id]
        if conv.topic == topic:
            return conv_id
    raise Exception('chat not found')


def uuid_decode(b64uuid):
    ub = base64.urlsafe_b64decode(b64uuid + '==')
    uobj = uuid.UUID(bytes=ub)
    return str(uobj)


def process_msg(fc, chat, msg):
    if msg.mk_message_type == 'text':
        txt = convert_xml_to_text(msg.message).strip()
        print("got msg: %r" % msg.__dict__)
        chat.mark_read(msg.message_nr)
        print('text: %s' % txt)
        if txt[:1] == "!":
            chat.message_send(str(query(txt[1:])))


def query(input):
    print("Request:    " + input)
    response = r.request("GET", backend_url + input)
    print("Response:   " + response.text)
    return response.text


def get_chat_id(fc):
    chat_id = None
    if CHAT_TOPIC is not None:
        chat_id = find_chat_by_topic(fc, CHAT_TOPIC)

    if chat_id is None and CHAT_CID is not None:
        chat_id = uuid_decode(CHAT_CID)

    if chat_id is None:
        raise Exception('need chat info')
    return chat_id


def main():
    username, password = load_config()

    print('Login')
    fc = FleepCache(SERVER, username, password)
    print('Loading contacts')
    print('convs: %d' % len(fc.conversations))

    chat_id = get_chat_id(fc)
    chat = fc.conversations[chat_id]
    print('chat_id: %s' % chat_id)

    chat_msg_nr = chat.read_message_nr

    while True:
        while True:
            msg = chat.get_next_message(chat_msg_nr)
            if not msg:
                break
            process_msg(fc, chat, msg)
            chat_msg_nr = msg.message_nr

        if not fc.poll():
            time.sleep(1)
            continue


if __name__ == '__main__':
    main()

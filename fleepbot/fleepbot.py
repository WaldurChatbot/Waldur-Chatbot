# Derived from https://github.com/fleephub/fleep-api/blob/master/python-client/chatbot.py

#import urlparse
import uuid
import base64
import time
import requests as r

from fleepclient.cache import FleepCache
from fleepclient.utils import convert_xml_to_text

backend_url = "http://localhost:4567/"

SERVER = 'https://fleep.io'
# how to identify chat
CHAT_URL = None #"https://fleep.io/chat?cid=exdMtzePSNCb2zQwfOwVFA"             # https://fleep.io/chat?cid=P6lD79k_TMSYwg8AAbX6Tg
CHAT_TOPIC = "Api send test"           # 'bot-test'


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


def main():
    USERNAME, PASSWORD = load_config()

    print('Login')
    fc = FleepCache(SERVER, USERNAME, PASSWORD)
    print('Loading contacts')
    #fc.contacts.sync_all()
    print('convs: %d' % len(fc.conversations))

    if CHAT_TOPIC:
        chat_id = find_chat_by_topic(fc, CHAT_TOPIC)
    #elif CHAT_URL:
    #    p = urlparse.urlparse(CHAT_URL)
    #    q = urlparse.parse_qs(p.query)
    #    chat_id = uuid_decode(q['cid'][0])
    else:
        raise Exception('need chat info')

    chat = fc.conversations[chat_id]
    print('chat_id: %s' % chat_id)

    chat_msg_nr = chat.read_message_nr
    while 1:
        while 1:
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

#!/usr/bin/env python
# coding: utf-8

from telegram.ext import Updater, MessageHandler, Filters
import requests as r
import json

backend_url = "http://localhost:4567"

def query(bot, update):
    if update.message.text[:1] == '!':
        query = update.message.text[1:]
        print("Request:    " + query)
        response = r.request(
                "POST",
                backend_url,
                data={'query': query}
        ).text
        print("Response: " + response.strip())
        response = json.loads(response)

        if 'message' in response:
            response = response['message']
        else:
            response = "Something went wrong, sorry!"

        print("Response: " + response)
        update.message.reply_text(response)


def main():
    updater = Updater(read_token())

    dp = updater.dispatcher

    # responds to any message that starts with '!'
    dp.add_handler(MessageHandler(Filters.text, query))

    updater.start_polling()

    updater.idle()


def read_token():
    with open('.token', 'r') as token:
        return token.read()


if __name__ == '__main__':
    main()

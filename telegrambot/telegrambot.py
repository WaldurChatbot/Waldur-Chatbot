#!/usr/bin/env python
# coding: utf-8

from telegram.ext import Updater, MessageHandler, Filters
import requests as r

#
# pip install python-telegram-bot --upgrade
# Is most likely necessary for telegram.ext
#

backend_url = "http://localhost:4567/"


def query(bot, update):
    if update.message.text[:1] == '!':
        print("Request:    " + update.message.text[1:])
        response = r.request("GET", backend_url + update.message.text[1:])
        print("Response:   " + response.text)
        update.message.reply_text(response.text)


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

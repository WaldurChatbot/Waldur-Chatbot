#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.insert(0, '../')  # important for common import
from common import request

from telegram.ext import Updater, MessageHandler, Filters
import logging, logging.config, logging.handlers
from configparser import ConfigParser


def query(bot, update):
    if update.message.text[:1] == '!':
        query = update.message.text[1:]
        print("Query:    " + query)
        response = request.query(query)
        print("Response: " + str(response))
        update.message.reply_text(response['message'])


def main():
    config = ConfigParser()
    config.read('../configuration.ini')
    token = config['telegram']['token']

    updater = Updater(token)

    dp = updater.dispatcher

    # responds to any message that starts with '!'
    dp.add_handler(MessageHandler(Filters.text, query))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

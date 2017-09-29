#!/usr/bin/env python
# coding: utf-8

from telegram.ext import Updater, MessageHandler, Filters
import sys
import logging, logging.config, logging.handlers
sys.path.insert(0, '../')
from common import request
from configparser import ConfigParser

logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)

root = logging.getLogger(__name__)

def query(bot, update):
    if update.message.text[:1] == '!':
        query = update.message.text[1:]
        #print("Query:    " + query)
        response = request.query(query)
        #print("Response: " + str(response))
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

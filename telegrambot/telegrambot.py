#!/usr/bin/env python
# coding: utf-8
import sys
sys.path.insert(0, '../')  # important for common import

from telegram.ext import Updater, MessageHandler, Filters
import logging, logging.config, logging.handlers
from common import request
from configparser import ConfigParser

logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)

log = logging.getLogger("Telegram")


def query(bot, update):
    log.debug("IN: " + update.message.text)
    if update.message.text[:1] == '!':
        query = update.message.text[1:]
        log.info("IN:  " + query)
        response = request.query(query)
        log.info("OUT: " + response['message'])
        update.message.reply_text(response['message'])


def main():
    log.info("Initializing bot")
    config = ConfigParser()
    config.read('../configuration.ini')
    token = config['telegram']['token']

    updater = Updater(token)

    dp = updater.dispatcher
    log.info("Adding handlers")
    # responds to any message that starts with '!'
    dp.add_handler(MessageHandler(Filters.text, query))

    log.info("Starting polling")
    updater.start_polling()

    log.info("Bot initialized")
    updater.idle()


if __name__ == '__main__':
    main()

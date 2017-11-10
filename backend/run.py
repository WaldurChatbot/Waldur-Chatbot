import sys
import traceback
from configparser import ConfigParser
from logging import getLogger
from logging.config import fileConfig
from os import path

# general conf
config = ConfigParser()
config.read('../configuration.ini')
port = config['backend']['port']

# logging conf
log_file_path = path.join(path.dirname(path.abspath(__file__)), '..', 'logging_config.ini')
fileConfig(log_file_path, disable_existing_loggers=False)

log = getLogger(__name__)

# insert backend and common to path
sys.path.insert(0, '../')


if __name__ == '__main__':
    try:
        from backend.waldur.waldur import init_api, init_bot, train_bot

        chatbot = init_bot()
        train_bot(chatbot)

        api = init_api(chatbot)
        app = api.app

        log.info("Launching WaldurChatbot API on port {}".format(port))
        app.run(port=port)
    except:
        log.critical("Unresumable exception occurred")
        for line in traceback.format_exc().split("\n"): log.critical(line)
    finally:
        log.info("Shutting down")

import os
import sys
from configparser import ConfigParser
from logging import getLogger
from logging.config import fileConfig

fileConfig('../logging_config.ini')
log = getLogger(__name__)

# If config file location is setup in environment variables
# then read conf from there, otherwise from project root
if 'WALDUR_CONFIG' in os.environ:
    config_path = os.environ['WALDUR_CONFIG']
else:
    config_path = '../configuration.ini'

log.info("Reading config from {}".format(config_path))
config = ConfigParser()
config.read(config_path)

# insert backend and common to path
sys.path.insert(0, '../')

if __name__ == '__main__':
    try:
        from backend.waldur.waldur import init_api, init_bot, train_bot

        chatbot = init_bot()
        train_bot(chatbot)

        api = init_api(chatbot)
        app = api.app

        port = int(config['backend']['port'])
        log.info(f"Launching WaldurChatbot API on port {port}")
        app.run(port=port)
    except Exception as e:
        log.critical("Unresumable exception occurred")
        log.exception(e)
    finally:
        log.info("Shutting down")

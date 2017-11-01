import sys
import traceback
from configparser import ConfigParser
from logging import getLogger
from logging.config import fileConfig
from os import path

# read logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), '..', 'logging_config.ini')
fileConfig(log_file_path, disable_existing_loggers=False)

log = getLogger(__name__)

# insert backend and common to path
sys.path.insert(0, '../')

# import waldur flask app
from backend.waldur.waldur import app

config = ConfigParser()
config.read('../configuration.ini')
port = config['backend']['port']

if __name__ == '__main__':
    try:
        log.info("Launching Backend")
        app.run(port=port)
    except:
        log.critical("Unresumable exception occurred")
        for line in traceback.format_exc().split("\n"): log.critical(line)
    finally:
        log.info("Shutting down")

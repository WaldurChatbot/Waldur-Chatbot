from os import path
import sys  # for easily importing common
sys.path.insert(0, '../')

from logging import getLogger
from logging.config import fileConfig
log_file_path = path.join(path.dirname(path.abspath(__file__)), '..', 'logging_config.ini')
fileConfig(log_file_path, disable_existing_loggers = False)

__version__ = '0.1.5'

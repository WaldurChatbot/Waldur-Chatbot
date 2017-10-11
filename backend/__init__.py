import sys  # for easily importing common
sys.path.insert(0, '../')

import logging, logging.config, logging.handlers
logging.config.fileConfig('../logging_config.ini', disable_existing_loggers = False)


__version__ = '0.1.2'


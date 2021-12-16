import logging
from Childe.config import logger_config

class Logger(object):

    def __init__(self, level, path, **kv_args):

        log_levels = {
            "DEBUG"    : logging.DEBUG,
            "INFO"     : logging.INFO,
            "WARNING"  : logging.WARNING,
            "ERROR"    : logging.ERROR,
            "CRITICAL" : logging.CRITICAL
        }

        self.logging_methods = {
            "DEBUG"    : logging.debug,
            "INFO"     : logging.info,
            "WARNING"  : logging.warning,
            "ERROR"    : logging.error,
            "CRITICAL" : logging.critical
        }

        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            filename=path, level=log_levels[level], format=LOG_FORMAT, 
            datefmt=DATE_FORMAT
        )

    def log(self, level, message):
        self.logging_methods[level](message)
        
logger = Logger(**logger_config)

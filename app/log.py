import logging
import sys
import os
import time
from functools import wraps
from colorlog import ColoredFormatter
from ierror import APP_NAME


os.makedirs("logs", exist_ok=True)

logName = f"{os.path.dirname(os.path.abspath(__file__))}/logs/{APP_NAME}-{str(time.strftime('%Y-%m-%d'))}.log"


class Logger:
    _instance = None

    def __new__(cls, output: str = "stdout"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = cls._instance.setup_logger(output)
        return cls._instance

    def setup_logger(self, output):
        # set the log level to DEBUG
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        # Create a formatter with the desired log format
        log_format = "%(asctime)s  %(levelname)-8s | %(message)s"
        formatter = logging.Formatter(log_format)
        if output == "stdout":
            # Create a colored formatter for console output
            console_formatter = ColoredFormatter(
                "%(log_color)s%(asctime)s | %(levelname)-5s%(reset)s | %(log_color)s%(message)s%(reset)s"
            )
            # support stdout
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        else:
            # Create a file handler and logs path
            file_handler = logging.FileHandler(logName)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def set_log_level(self, module_name, level):
        module_logger = logging.getLogger(module_name)
        module_logger.setLevel(level)

    # def set_apscheduler_log_level(self, level):
    #     apscheduler_logger = logging.getLogger('apscheduler')
    #     apscheduler_logger.setLevel(level)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
        exit(1)

    def fatal(self, msg):
        self.logger.fatal(msg)
        exit(1)


def log_method(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        logger = Logger()
        logger.info(f"Calling  [{func.__name__}] with args: {args}, kwargs: {kwargs}")
        try:
            result = func(self, *args, **kwargs)
            logger.info(f"Function [{func.__name__}] returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Function [{func.__name__}] raised an exception: {str(e)}")

    return wrapper

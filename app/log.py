import logging
import sys
import os
import time
import asyncio
from functools import wraps
from colorlog import ColoredFormatter


class Logger:
    _instance = None

    def __new__(cls, level="INFO"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = cls._instance.setup_logger(level)
        return cls._instance

    def setup_logger(self, level):

        logger = logging.getLogger("wealert")

        if logger.handlers:
            return logger

        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
        logger.propagate = False

        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)

        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)-5s%(reset)s | %(log_color)s%(message)s%(reset)s"
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def set_level(self, level):
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def fatal(self, msg):
        self.logger.fatal(msg)

    def exception(self, msg):
        self.logger.exception(msg)


logger = Logger()


def WeLog(func):
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cls = args[0].__class__.__name__ if args else ""
            logger.debug(
                f"calling [{cls}.{func.__name__}] args={args[1:]}, kwargs={kwargs}"
            )
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"function [{cls}.{func.__name__}] returned: {result}")
                return result
            except Exception as e:
                if not getattr(e, "_we_logged", False):
                    e._we_logged = True
                    logger.exception(f"function [{cls}.{func.__name__}] execute failed")
                raise

        return async_wrapper

    @wraps(func)
    def wrapper(*args, **kwargs):
        cls = args[0].__class__.__name__ if args else ""
        logger.debug(
            f"calling [{cls}.{func.__name__}] args={args[1:]}, kwargs={kwargs}"
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(f"function [{cls}.{func.__name__}] returned: {result}")
            return result
        except Exception as e:
            if not getattr(e, "_we_logged", False):
                e._we_logged = True
                logger.exception(f"function [{cls}.{func.__name__}] execute failed")
            raise

    return wrapper

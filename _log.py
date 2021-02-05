import sys
import logging
from loguru import logger


_fmt="{time:YYYY-MM-DD at HH:mm:ss} | <level>{message}</level> |  <yellow>metadata:</yellow> {extra[meta]} (?){extra[surplus]}"

def _set_loggers(verbosity: int = 2, api_verbosity: str = 'DEBUG') -> None:
    """
    Set the logging level for third party libraries
    :return: None
    """

    logging.getLogger('requests').setLevel(
        logging.INFO if verbosity <= 1 else logging.DEBUG
    )
    logging.getLogger("urllib3").setLevel(
        logging.INFO if verbosity <= 1 else logging.DEBUG
    )
    logging.getLogger('ccxt.base.exchange').setLevel(
        logging.INFO if verbosity <= 2 else logging.DEBUG
    )
    logging.getLogger('telegram').setLevel(logging.INFO)

def setup_logging(log: dict) -> None:
    # _fmt="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message} {meta}"
    # logging.basicConfig(handlers=[InterceptHandler()], level=0)
    _set_loggers()
    config = {
        'handlers': [
            {"sink": sys.stdout, "format": _fmt, 'level': log['level']},
            {"sink": log['file'], "serialize": True, 'level': log['level']},
        ],
        'extra': {'meta': {}, 'surplus': {}}
    }

    return config


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
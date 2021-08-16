from pythonjsonlogger import jsonlogger
from datetime import datetime
import logging
from logging.config import dictConfig


class ElkJsonFormatter(jsonlogger.JsonFormatter):
    """
    ELK stack-compatibile formatter
    """

    def add_fields(self, log_record, record, message_dict):
        super(ElkJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["@timestamp"] = datetime.now().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name


def create_logger(logger_name: str, log_filename: str = "./logs.json"):
    """
    Creates a logger instance
    """
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                # exact format is not important, this is the minimum information
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            },
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                "log_colors": {
                    "DEBUG": "white",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bold",
                },
            },
            "colored_db": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                "log_colors": {
                    "DEBUG": "purple",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bold",
                },
            },
            "json_formatter": {
                "()": "seedwork.infrastructure.logging.ElkJsonFormatter",
            },
        },
        "handlers": {
            # console logs to stderr
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "colored_console": {
                "class": "colorlog.StreamHandler",
                "formatter": "colored",
            },
            "colored_console_db": {
                "class": "colorlog.StreamHandler",
                "formatter": "colored_db",
            },
            "file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_filename,
                "formatter": "json_formatter",
            }
            if log_filename
            else None,
            # Add Handler for Sentry for `warning` and above
            # 'sentry': {
            #     'level': 'WARNING',
            #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            # },
        },
        "loggers": {
            logger_name: {
                "level": "DEBUG",
                "handlers": ["colored_console", "file_handler"],  # , 'sentry'],
            },
            # Prevent noisy modules from logging to Sentry
            "noisy_module": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    dictConfig(logging_config)
    logger = logging.getLogger(name=logger_name)
    return logger

from pythonjsonlogger import jsonlogger
from datetime import datetime
import logging
from logging import Logger
from logging.config import dictConfig
from seedwork.utils.functional import SimpleLazyObject
from seedwork.infrastructure.request_context import request_context


class RequestContextFilter(logging.Filter):
    """ "Provides correlation id parameter for the logger"""

    def __init__(self, name: str, request_context) -> None:
        super().__init__(name=name)
        self.request_context = request_context

    def filter(self, record):
        record.correlation_id = self.request_context.correlation_id.get()
        return True


class ElkJsonFormatter(jsonlogger.JsonFormatter):
    """
    ELK stack-compatibile formatter
    """

    def add_fields(self, log_record, record, message_dict):
        super(ElkJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["@timestamp"] = datetime.now().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name


class LoggerFactory:
    _configured = False

    @classmethod
    def configure(
        cls,
        logger_name="app",
        log_filename="./logs.json",
        request_context=request_context,
    ):
        cls.logger_name = logger_name
        cls.log_filename = log_filename
        cls.request_context = request_context
        cls._configured = True

    @classmethod
    def create_logger(cls):
        """
        Returns a logger instance, based on a configuration options
        """
        if not cls._configured:
            cls.configure()
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    # exact format is not important, this is the minimum information
                    "format": "%(asctime)s %(name)-12s %(levelname)-8s %(correlation_id)s %(message)s",
                },
                "colored": {
                    "()": "colorlog.ColoredFormatter",
                    "format": "%(log_color)s%(asctime)s %(name)-12s %(levelname)-8s %(correlation_id)s %(message)s",
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
                    "format": "%(log_color)s%(asctime)s %(name)-12s %(levelname)-8s %(correlation_id)s %(message)s",
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
                    "filename": cls.log_filename,
                    "formatter": "json_formatter",
                }
                if cls.log_filename
                else None,
                # Add Handler for Sentry for `warning` and above
                # 'sentry': {
                #     'level': 'WARNING',
                #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                # },
            },
            "loggers": {
                cls.logger_name: {
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
        logger = logging.getLogger(name=cls.logger_name)
        logger.addFilter(
            RequestContextFilter(
                name=cls.logger_name, request_context=cls.request_context
            )
        )
        return logger


"""
We are making logger globally available, but to make it configurable logger lazy-evaluated.
Use `LoggerFactory.configure()` to configure the logger prior to its usage
"""
logger = SimpleLazyObject(LoggerFactory.create_logger)

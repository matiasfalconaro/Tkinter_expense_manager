import logging
import os

from logging.config import dictConfig


def setup_logging() -> None:
    """Initializes and configures the logging system for the application."""
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    logging_config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s][%(name)s][%(levelname)s][%(message)s]'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': logging.DEBUG
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(log_directory, 'app.log'),
                'formatter': 'standard',
                'level': logging.DEBUG
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': logging.DEBUG,
                'propagate': False
            }
        }
    }

    dictConfig(logging_config)

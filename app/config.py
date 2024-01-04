import logging
from logging.config import dictConfig

def setup_logging():
    logging_config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s][%(name)s][%(levelname)s] - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': logging.DEBUG
            },
            # Add file handler to log to a file 
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': logging.DEBUG,
                'propagate': False
            }
        }
    }

    dictConfig(logging_config)

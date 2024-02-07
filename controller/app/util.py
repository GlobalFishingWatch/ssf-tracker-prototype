# Utilities

import ujson as json
import logging
from copy import deepcopy
try:
    import uerrno as errno
except ImportError or ModuleNotFoundError:
    import errno

from timer import Timer
from config import default_config


def load_config(settings):
    """
    Load app settings into a dict.  Missing values will be copied from default_config

    :param settings: can be one of three possible types
      * The name of a local file containing json
      * A json string
      * a python dict

    :return: a dict
    """
    config = deepcopy(default_config)
    if isinstance(settings, dict):
        config.update(settings)
    else:
        if settings.startswith('{'):
            # assume that a json string was passed in
            config.update(json.loads(settings))
        else:
            try:
                config['SETTINGS_FILE'] = settings
                with open(settings, 'r') as f:
                    config.update(json.load(f))
            except OSError as err:
                msg = str(err)
                if err.errno == errno.ENOENT:
                    # override the built in message so it is the same when using either python or micropython
                    # python: "[Errno 2] No such file or directory: 'not-found.json'"
                    # micropython: "[Errno 2] ENOENT"
                    msg = f'File not found "{settings}"'
                config['SETTINGS_LOAD_STATUS'] = msg

    return config


def save_config(config, dest_file_name):
    """
    Serialize the given dict and write to the given local file
    :param config: A dict with json-serializable values
    :param dest_file_name: A local file name
    :return: None
    """
    with open(dest_file_name, 'w') as f:
        json.dump(config, f)


class LogFormatter(logging.Formatter):
    def formatTime(self, record, datefmt):
        return f'{Timer.current_time_ms()/1000:.3f}'


log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}


def configure_logger(config):
    # get the log level to use
    level = log_levels.get(config.get('LOG_LEVEL', 'INFO').upper(), 'logging.INFO')
    formatter = LogFormatter("%(asctime)s %(message)s")

    # get the default logger
    logger = default_logger()
    logger.setLevel(level)

    # create a handler that writes to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # create a handler that writes to a file
    filename = config.get('LOG_FILE')
    if filename:
        # default_handler = log.handlers[0]
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def default_logger():
    return logging.getLogger('root')

import sys
import json
import logging


from timer import Timer


def load_config(source_file_name):
    try:
        with open(source_file_name, 'r') as f:
            return json.load(f)
    except OSError:
        return {}

def save_config(config, dest_file_name):
    with open(dest_file_name, 'w') as f:
        json.dump(config, f)


class LogFormatter(logging.Formatter):
    def formatTime(self, record, datefmt):
        # record.asctime = f'{Timer.current_time_ms()/1000}'
        return f'{Timer.current_time_ms()/1000:.3f}'


log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}

def configure_logger(config):
    # get the log level to use
    level = log_levels.get(config.get('log-level', 'INFO').upper(), 'logging.INFO')
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
    filename=config.get('log-file')
    if filename:
        # default_handler = log.handlers[0]
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def default_logger():
    return logging.getLogger('root')

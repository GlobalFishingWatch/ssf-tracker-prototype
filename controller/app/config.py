import os
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


log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}

def configure_logger(config):
    level = log_levels.get(config['log-level'].upper(), 'logging.INFO')
    format = '%(message)s'
    logging.basicConfig(level=level, format=format)
    log = logging.getLogger('root')
    filename=config.get('log-file')
    if filename:
        default_handler = log.handlers[0]
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(default_handler.level)
        file_handler.setFormatter(default_handler.formatter)
        log.addHandler(file_handler)
    return log

def default_logger():
    return logging.getLogger('root')

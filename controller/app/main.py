# main.py
# this is the main app for the microcontroller
# runs after boot.py

from config import load_cofig
from config import configure_logger
from timer import Timer

# DEFAULT CONFIG SETTINGS
app_config = {
    'log-level': 'DEBUG',
    'log-file': 'log.txt'
}

# OVERWRITE DEFAULTS FROM SAVED CONFIG FILE
config_filename = './config.json'
app_config.update(load_cofig(config_filename))

log = configure_logger(app_config)
log.info('Starting App...')

t = Timer()
log.debug(t._get_time_ms())
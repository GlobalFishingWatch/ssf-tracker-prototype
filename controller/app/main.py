# main.py
# this is the main app for the microcontroller
# runs after boot.py

from config import load_config
from config import configure_logger
from app import App
from wiring_esp32 import WiringESP32

# DEFAULT CONFIG SETTINGS
app_config = {
    'log-level': 'DEBUG',
    'log-file': 'log.txt',
    'loop_sleep_time_ms': 10,
    'LED1_PIN': 5,
    'BTN1_PIN': 4,
}

# OVERWRITE DEFAULTS FROM SAVED CONFIG FILE
config_filename = './config.json'
app_config.update(load_config(config_filename))

log = configure_logger(app_config)
log.info('Starting App...')


app = App(WiringESP32, log=log, config=app_config)
app.initialize()
# app.run()


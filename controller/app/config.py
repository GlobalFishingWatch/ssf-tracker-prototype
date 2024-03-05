# App Settings

default_app_state = {
    'state': 'boot',
    'idle_timer': {'active': False, 'deadline': 0},
    'gps_timer': {'active': False, 'deadline': 0},
    'button1': {'state': 'released', 'timer': {'active': False, 'deadline': 0}},
    'locations': []
}

# DEFAULT CONFIG SETTINGS
default_config = {
    'LOG_LEVEL': 'DEBUG',
    'LOG_FILE': 'log.txt',
    'LOCATION_FILE': 'locations.txt',
    'LED1_PIN': 5,
    'BTN1_PIN': 15,
    'BTN2_PIN': 14,
    'RGB_PIN': 0,
    'IDLE_TIMEOUT_MS': 10 * 1000,
    'GPS_FIX_INTERVAL_MS': 25 * 1000, #5 * 60 * 1000,
    'RETRY_INTERVAL_MS': 10 * 1000,
    'MIN_LIGHTSLEEP_TIME_MS': 100,
    'MAX_LIGHTSLEEP_TIME_MS': 1000,
    'MIN_DEEPSLEEP_TIME_MS': 10 * 1000,
    'MAX_DEEPSLEEP_TIME_MS': 24 * 60 * 60 * 1000,
    'SETTINGS_FILE': None,
    'SETTINGS_LOAD_STATUS': 'ok',
    'app_state': default_app_state,
}
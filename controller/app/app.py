# Main application

from config import default_logger
from config import load_config
from config import save_config
from config import configure_logger

from statemachine import StateMachine
from statemachine import State
from statemachine import Transition
from statemachine import Event
from button import Button
from timer import Timer
from gps import MockGPS

from wiring import MockWiring

class App(StateMachine):
    states = [
        State('boot'),
        State('idle', on_enter='on_idle'),
        State('locating', on_enter='on_locating'),
        State('sleep', on_enter='on_sleep'),
    ]
    transitions = [
        Transition(event='reset', source='boot', dest='idle', after='on_reset'),
        Transition(event='idle_timeout', source='idle', dest='sleep'),
        Transition(event='timer_wake', source='sleep', dest='idle'),
        Transition(event='btn_wake', source='sleep', dest='idle'),
        Transition(event='btn1_pressed', after='on_btn1_pressed'),
        Transition(event='btn1_released', after='on_btn1_released'),
        Transition(event='gps_timer', source='idle', dest='locating', after='on_gps_timer'),
        Transition(event='gps_ready', source='locating', dest='idle', before='on_gps_ready'),

        # Always call on_gps_timer no matter what state we're in
        Transition(event='gps_timer', after='on_gps_timer'),
    ]

    @classmethod
    def from_settings(cls, settings, wiring_type=MockWiring, **kwargs):
        app_config = load_config(settings)
        log = configure_logger(app_config)
        wiring = wiring_type(config=app_config)
        log.debug('Creating App...')
        app = cls(wiring=wiring, config=app_config, log=log, **kwargs)
        return app


    def __init__(self, wiring, config=None, log=None, **kwargs):
        self.wiring = wiring
        self.config = config if config else {}
        self.log = log if log else default_logger()
        super(App, self).__init__(states=self.states, transitions=self.transitions, log=self.log, **kwargs)

        self.button1 = Button(name="button1", log=self.log,
                              on_press_event=self.get_event('btn1_pressed'),
                              on_release_event=self.get_event('btn1_released'))

        self.idle_timer = Timer(event=self.get_event('idle_timeout'),
                                duration_ms=self.config.get('IDLE_TIMEOUT_MS', 10000))
        self.gps = MockGPS(on_ready_event=self.get_event('gps_ready'))
        self.gps_timer = Timer(event=self.get_event('gps_timer'),
                                duration_ms=self.config.get('GPS_FIX_INTERVAL_MS', 10000))
        self.locations = []

    def initialize(self):
        self.log.debug(f'{self.name} initialize...')
        self.wiring.btn_down_event=self.button1.get_event('btn_down')
        self.wiring.btn_up_event=self.button1.get_event('btn_up')
        self.wiring.initialize()
        wake_reason = self.wiring.wake_reason()
        self.log.debug(f'Wake reason: {wake_reason}')
        app_state = self.config.get('app_state')
        if wake_reason == 'RESET':
            self.get_event('reset').trigger()
        elif app_state:
            self.load_state(app_state)
        else:
            self.log.warning('App waking from sleep but no saved app state found')
            self.get_event('reset').trigger()


    def settings_file_name(self):
        return self.config['SETTINGS_FILE']

    def is_running(self):
        return True

    def get_sleep_time_ms(self, min_time, max_time):
        timer = Timer.get_next_timer()
        sleep_time =  min(timer.time_remaining_ms(), max_time) if timer else max_time
        return sleep_time if sleep_time > min_time else 0

    def lightsleep(self):
        min_time = self.config.get('MIN_LIGHTSLEEP_TIME_MS', 100)
        max_time = self.config.get('MAX_LIGHTSLEEP_TIME_MS', 1000)
        sleep_time = self.get_sleep_time_ms(min_time, max_time)
        if sleep_time:
            self.wiring.lightsleep(sleep_time)

    def run(self):
        self.log.debug(f'{self.name} run...')
        while self.is_running():
            Timer.check_active_timers()
            Event.trigger_scheduled_events()
            self.lightsleep()

    @staticmethod
    def tick():
        Timer.check_active_timers()
        Event.trigger_scheduled_events()

    def on_reset(self, event):
        self.gps_timer.reset()

    def on_idle(self, event):
        self.idle_timer.reset()

    def can_deep_sleep(self):
        # we can only go into deep sleep if the gps is not active
        return self.gps.state.name == "sleep"

    def on_sleep(self, event):
        self.idle_timer.cancel()
        min_time = self.config.get('MIN_DEEPSLEEP_TIME_MS', 100)
        max_time = self.config.get('MAX_DEEPSLEEP_TIME_MS', 1000)
        sleep_time = self.get_sleep_time_ms(min_time, max_time)

        if sleep_time and self.can_deep_sleep():
            # Prepare for deep sleep which will restart the application
            self.config['app_state'] = self.save_state()
            filename = self.settings_file_name()
            if filename:
                save_config(self.config, self.settings_file_name)
            else:
                self.log.debug('Skipping saving settings because no file name is configured')

            # NB: this will sleep for the specified time and then reset the app
            # NB: Control flow will never return from this call unless you are using MockWiring
            self.wiring.deepsleep(sleep_time)
        else:
            # not enough time to sleep before the next timer goes off
            # so trigger the wake event immediately
            self.get_event('timer_wake').trigger()

    def on_btn1_pressed(self, event):
        self.wiring.led1 = 1

    def on_btn1_released(self, event):
        self.wiring.led1 = 0

    def on_locating(self, event):
        # start to fix a new gps location
        self.gps.schedule_event('locate')
        self.gps_timer.reset(duration_ms=self.config.get('GPS_FIX_INTERVAL_MS',10000))

    def on_gps_timer(self, event):
        if self.state.name != 'locating':
            # The timer went off but we are not in a state where we can activate the GPS,
            # so try again later
            self.gps_timer.reset(duration_ms=self.config.get('APP_BUSY_WAIT_INTERVAL_MS',10000))

    def on_gps_ready(self, event):
        self.locations.append(self.gps.last_location)
        self.gps.schedule_event('sleep')

    def save_state(self):
        state = super(App, self).save_state()
        state['button1'] = self.button1.save_state()
        state['idle_timer'] = self.idle_timer.save_state()
        return state

    def load_state(self, state):
        self.button1.load_state(state['button1'])
        self.idle_timer.load_state(state['idle_timer'])
        super(App, self).load_state(state)
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
        State('sleep', on_enter='on_sleep'),
    ]
    transitions = [
        Transition(event='reset',  source='boot', dest='idle'),
        Transition(event='idle_timeout', source='idle', dest='sleep'),
        Transition(event='timer_wake', source='sleep', dest='idle'),
        Transition(event='btn_wake', source='sleep', dest='idle'),
        Transition(event='btn1_pressed', after='on_btn1_pressed'),
        Transition(event='btn1_released', after='on_btn1_released'),
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

    def initialize(self):
        self.log.debug(f'{self.name} initialize...')
        self.wiring.btn_down_event=self.button1.get_event('btn_down')
        self.wiring.btn_up_event=self.button1.get_event('btn_up')
        self.wiring.initialize()
        # TODO: get the wake reason from wiring
        #       if we are waking from sleep then restore saved state
        #       if not then trigger the 'reset' event to move us from boot to idle

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

    def on_idle(self, event):
        self.idle_timer.reset()

    def on_sleep(self, event):
        min_time = self.config.get('MIN_DEEPSLEEP_TIME_MS', 100)
        max_time = self.config.get('MAX_DEEPSLEEP_TIME_MS', 1000)
        sleep_time = self.get_sleep_time_ms(min_time, max_time)
        if sleep_time:
            # Prepare for deep sleep which will restart the application
            self.config['app_state'] = self.save_state()
            filename = self.settings_file_name()
            if filename:
                save_config(self.config, self.settings_file_name)
            else:
                self.log.debug('Skipping saving settings because not file name is configured')

            # NB: this will sleep for the specified time and then reset the app
            # control flow will never return from this call unless you are using MockWiring
            self.wiring.deepsleep(sleep_time)
        else:
            # not enough time to sleep before the next timer goes off
            # so trigger the wake event immediately
            self.get_event('timer_wake').trigger()

    def on_btn1_pressed(self, event):
        self.wiring.led1 = 1

    def on_btn1_released(self, event):
        self.wiring.led1 = 0

    def save_state(self):
        state = super(App, self).save_state()
        state['button1'] = self.button1.save_state()
        state['idle_timer'] = self.idle_timer.save_state()
        return state

    def load_state(self, state):
        self.button1.load_state(state['button1'])
        self.idle_timer.load_state(state['idle_timer'])
        super(App, self).load_state(state)
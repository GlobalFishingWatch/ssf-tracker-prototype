# Main application

from config import default_logger

from statemachine import StateMachine
from statemachine import State
from statemachine import Transition
from statemachine import Event
from button import Button
from timer import Timer


class App(StateMachine):
    states = [
        State('boot'),
        State('idle', on_enter='on_idle'),
        State('sleep', on_enter='on_sleep'),
    ]
    transitions = [
        Transition(event='btn1_pressed', after='on_btn1_pressed'),
        Transition(event='btn1_released', after='on_btn1_released'),
        Transition(event='idle_timeout', source='idle', dest='sleep'),
    ]

    def __init__(self, WiringType, config=None, log=None,  **kwargs):
        self.config = config if config else {}
        self.log = log if log else default_logger()
        super(App, self).__init__(states=self.states, transitions=self.transitions, log=self.log, **kwargs)

        self.button1 = Button(name="button1", log=self.log,
                              on_press_event=self.get_event('btn1_pressed'),
                              on_release_event=self.get_event('btn1_released'))

        self.wiring = WiringType(config=self.config,
                                 btn1_up_event=self.button1.get_event('btn_up'),
                                 btn1_down_event=self.button1.get_event('btn_down'))
        self.idle_timer = Timer(event=self.get_event('idle_timeout'), duration_ms=self.config.get('IDLE_TIMEOUT_MS', 10000))

    def initialize(self):
        self.log.debug(f'{self.name} initialize...')
        self.wiring.initialize()

    def run(self):
        self.log.debug(f'{self.name} run...')
        while True:
            self.tick()
            # self.wiring.lightsleep(self.config.get('loop_sleep_time_ms', 10))

    @staticmethod
    def tick():
        Timer.check_active_timers()
        Event.trigger_scheduled_events()

    def on_btn1_pressed(self, event):
        self.wiring.led1 = 1

    def on_btn1_released(self, event):
        self.wiring.led1 = 0

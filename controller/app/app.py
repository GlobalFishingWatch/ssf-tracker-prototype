# Main application

from config import default_logger

from wiring import Wiring
from statemachine import StateMachine
from statemachine import State
from statemachine import Transition
from button import Button
from timer import Timer


class App(StateMachine):
    states = [
        State('setup'),
    ]
    transitions = [
        Transition(event='btn1_pressed', after='on_btn1_pressed'),
        Transition(event='btn1_released', after='on_btn1_released'),
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


    def initialize(self):
        self.log.debug(f'{self.name} initialize...')
        self.wiring.initialize()

    def run(self):
        self.log.debug(f'{self.name} run...')
        while True:
            Timer.check_active_timers()
            # self.wiring.lightsleep(self.config.get('loop_sleep_time_ms', 10))


    def on_btn1_pressed(self, event):
        self.wiring.led1 = 1

    def on_btn1_released(self, event):
        self.wiring.led1 = 0

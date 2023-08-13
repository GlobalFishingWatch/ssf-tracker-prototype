# A state machine for de-boucing a hardware button

import time

from statemachine import StateMachine
from statemachine import State
from statemachine import Transition
from statemachine import EventData
from timer import Timer


event_press = 'press'
event_release = 'release'

class Button(StateMachine):
    states = [
        State('released', on_enter='stop_timer'),
        State('pressing', on_enter='start_timer'),
        State('pressed', on_enter='stop_timer'),
        State('releasing', on_enter='start_timer'),
    ]
    transitions = [
        Transition('released', 'pressing', 'btn_down'),
        Transition('pressing', 'released', 'btn_up'),
        Transition('pressing', 'pressed', 'timeout'),
        Transition('pressed', 'releasing', 'btn_up'),
        Transition('releasing', 'pressed', 'btn_down'),
        Transition('releasing', 'release', 'timeout'),
    ]

    def __init__(self, bounce_timeout_ms=10):
        self.bounce_timeout_ms = bounce_timeout_ms
        self.bounce_timer = Timer(event_data=EventData(machine=self), duration_ms=bounce_timeout_ms)
        super(Button, self).__init__(states=self.states, transitions=self.transitions)

    def start_timer(self, event_data):
        self.bounce_timer.reset()

    def stop_timer(self, event_data):
        self.bounce_timer.cancel()


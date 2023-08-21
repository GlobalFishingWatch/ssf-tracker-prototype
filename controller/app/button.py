# A state machine for de-bouncing a hardware button

from statemachine import StateMachine
from statemachine import State
from statemachine import Transition
from timer import Timer


class Button(StateMachine):
    states = [
        State('released'),
        State('pressing', on_enter='start_timer'),
        State('pressed'),
        State('releasing', on_enter='start_timer'),
    ]
    transitions = [
        Transition('btn_down', 'released', 'pressing'),
        Transition('btn_up', 'pressing', 'released'),
        Transition('timeout', 'pressing', 'pressed', after='on_press'),
        Transition('btn_up', 'pressed', 'releasing'),
        Transition('btn_down', 'releasing', 'pressed'),
        Transition('timeout', 'releasing', 'released', after='on_release'),
    ]

    def __init__(self, bounce_timeout_ms=10, on_press_event=None, on_release_event=None, timer=None, **kwargs):
        super(Button, self).__init__(states=self.states, transitions=self.transitions, **kwargs)
        self.bounce_timeout_ms = bounce_timeout_ms
        self.on_press_event = on_press_event
        self.on_release_event = on_release_event
        self.bounce_timer = timer if timer else Timer(event=self.get_event('timeout'), duration_ms=bounce_timeout_ms)

    def start_timer(self, event_data):
        self.bounce_timer.reset()

    def stop_timer(self, event_data):
        self.bounce_timer.cancel()

    def on_press(self, event_data):
        self.bounce_timer.cancel()
        if self.on_press_event:
            self.on_press_event.trigger()

    def on_release(self, event_data):
        self.bounce_timer.cancel()
        if self.on_release_event:
            self.on_release_event.trigger()

# A state machine for de-bouncing a hardware button

from statemachine import StateMachine
from statemachine import State
from statemachine import Transition
from timer import Timer


class Button(StateMachine):
    states = [
        State('released', on_enter='on_release'),
        State('pressing', on_enter='start_timer'),
        State('pressed', on_enter='on_press'),
        State('releasing', on_enter='start_timer'),
    ]
    transitions = [
        Transition('released', 'pressing', 'btn_down'),
        Transition('pressing', 'released', 'btn_up'),
        Transition('pressing', 'pressed', 'timeout'),
        Transition('pressed', 'releasing', 'btn_up'),
        Transition('releasing', 'pressed', 'btn_down'),
        Transition('releasing', 'released', 'timeout'),
    ]

    def __init__(self, bounce_timeout_ms=10, on_press_event=None, on_release_event=None, timer=None):
        self.bounce_timeout_ms = bounce_timeout_ms
        self.on_press_event = on_press_event
        self.on_release_event = on_release_event
        self.bounce_timer = timer if timer else Timer(event=self.get_event('timeout'), duration_ms=bounce_timeout_ms)
        super(Button, self).__init__(states=self.states, transitions=self.transitions)

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



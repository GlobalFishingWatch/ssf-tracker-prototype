# Satellite transmitter subsystem

from statemachine import State
from statemachine import Transition
from statemachine import StateMachine
from timer import Timer


class MockTransmitter(StateMachine):
    states = [
        State('sleep', on_enter='on_enter_sleep'),
        State('transmitting', on_enter='on_enter_transmitting'),
    ]
    transitions = [
        Transition('transmit', 'sleep', 'transmitting', after='transmit_message'),
        Transition('transmit_success', 'transmitting', 'sleep', before='on_transmit_success'),
        Transition('sleep', None, 'sleep'),
    ]

    def __init__(self, timeout_ms=10000, on_success_event=None, timer=None, **kwargs):
        super(MockTransmitter, self).__init__(states=self.states, transitions=self.transitions, **kwargs)
        self.timeout_ms = timeout_ms
        self.on_success_event = on_success_event
        self.transmit_timer = timer if timer else Timer(event=self.get_event('transmit_success'), duration_ms=self.timeout_ms)
        self._message = None

    def on_enter_transmitting(self, event):
        # start a timer that will transition us to ready
        self.transmit_timer.reset()

    def transmit_message(self, event):
        self._message = event.kwargs['message']

    def on_transmit_success(self, event):
        self.on_success_event.schedule()

    def on_enter_sleep(self, event):
        # cancel any running timer and clear the message
        # pretend to sleep
        self.transmit_timer.cancel()
        self._message = None


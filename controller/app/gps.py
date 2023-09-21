# GPS subsystem

from statemachine import State
from statemachine import Transition
from statemachine import StateMachine
from timer import Timer

class GPS(StateMachine):
    states = [
        State('sleep', on_enter='on_enter_sleep'),
        State('locating', on_enter='on_enter_locating'),
        State('ready', on_enter='on_enter_ready'),
        State('failed', on_enter='on_enter_failed'),
    ]
    transitions = [
        Transition('locate', 'sleep', 'locating'),
        Transition('gps_ready', 'locating', 'ready'),
        Transition('gps_ready', 'ready', None),
        Transition('sleep', None, 'sleep'),
    ]

    def __init__(self, wiring, on_ready_event=None, **kwargs):
        super(GPS, self).__init__(states=self.states, transitions=self.transitions, **kwargs)
        self.wiring = wiring
        self.on_ready_event = on_ready_event
        self.gps_fix_event = self.get_event('gps_ready')
        self._last_location = None

    @property
    def last_location(self):
        # get the most recent recorded location.  Could be None
        return self._last_location

    def on_enter_locating(self, event):
        # start a timer that will transition us to ready
        self.gps_timer.reset()

    def on_enter_ready(self, event):
        # pretend that we have fixed a GPS position
        self.gps_timer.cancel()
        self._last_location = dict (lat=22, lon=33, timestamp=Timer.current_time_ms())
        self.on_ready_event.trigger()

    def on_enter_sleep(self, event):
        # cancel any running timer and clear the last location
        # pretend to sleep
        self.gps_timer.cancel()
        self._last_location = None



#TODO: Deprecate this
class MockGPS(GPS):
    def __init__(self, **kwargs):
        super(MockGPS, self).__init__(**kwargs)


    @property
    def last_location(self):
        # get the most recent recorded location.  Could be None
        return self._last_location

    def on_enter_locating(self, event):
        # start a timer that will transition us to ready
        self.gps_timer.reset()

    def on_enter_ready(self, event):
        # pretend that we have fixed a GPS position
        self.gps_timer.cancel()
        self._last_location = dict (lat=22, lon=33, timestamp=Timer.current_time_ms())
        self.on_ready_event.trigger()

    def on_enter_sleep(self, event):
        # cancel any running timer and clear the last location
        # pretend to sleep
        self.gps_timer.cancel()
        self._last_location = None


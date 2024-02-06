# GPS subsystem

from statemachine import State
from statemachine import Transition
from statemachine import StateMachine
from timer import Timer
from machine import UART
import nmea


class MPYGPS(StateMachine):
    states = [
        State('sleep', on_enter='on_enter_sleep'),
        State('locating', on_enter='on_enter_locating'),
        State('ready', on_enter='on_enter_ready'),
    ]
    transitions = [
        Transition('locate', 'sleep', 'locating'),
        Transition('check_gps', after='on_check_gps'),
        Transition('gps_ready', 'locating', 'ready'),
        Transition('sleep', None, 'sleep'),

    ]

    def __init__(self, gps_timeout_ms=2000, on_ready_event=None, timer=None, baudrate=9600, tx=8, rx=7, **kwargs):
        super(MPYGPS, self).__init__(states=self.states, transitions=self.transitions, **kwargs)
        self.gps_timeout_ms = gps_timeout_ms
        self.on_ready_event = on_ready_event
        self.gps_timer = timer if timer else Timer(event=self.get_event('check_gps'), duration_ms=1000, recurring=True)
        self._last_location = None
        self.tx = tx
        self.rx = rx

        self.uart = UART(1, baudrate)
        self.uart.init(baudrate, tx=self.tx, rx=self.rx)

    @property
    def last_location(self):
        # get the most recent recorded location.  Could be None
        return self._last_location

    def on_enter_locating(self, event):
        # start a timer that will transition us to ready
        # if(gps
        self.gps_timer.reset()
        print("Enter Locating")

    def on_check_gps(self, event):
        # After event check_gps which is executed by timer
        # Check for fix: If fix, update location and trigger gps_ready
        msg_str = self.uart.readline().decode().strip()
        msg = nmea.parse_sentence(message_str)

        if msg['fix_quality'] == 1:
            self._last_location = msg
            self.get_event('gps_ready').trigger()

    def on_enter_ready(self, event):
        # If we have a fix, log message
        self.gps_timer.cancel()
        print("GPS READY")
        self.on_ready_event.trigger()

    def on_enter_sleep(self, event):
        # cancel any running timer and clear the last location
        # pretend to sleep
        self.gps_timer.cancel()
        self._last_location = None


class MockGPS(StateMachine):
    states = [
        State('sleep', on_enter='on_enter_sleep'),
        State('locating', on_enter='on_enter_locating'),
        State('ready', on_enter='on_enter_ready'),
    ]
    transitions = [
        Transition('locate', 'sleep', 'locating'),
        Transition('gps_ready', 'locating', 'ready'),
        Transition('sleep', None, 'sleep'),

    ]

    def __init__(self, gps_timeout_ms=2000, on_ready_event=None, timer=None, **kwargs):
        super(MockGPS, self).__init__(states=self.states, transitions=self.transitions, **kwargs)
        self.gps_timeout_ms = gps_timeout_ms
        self.on_ready_event = on_ready_event
        self.gps_timer = timer if timer else Timer(event=self.get_event('gps_ready'), duration_ms=self.gps_timeout_ms)
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
        self._last_location = dict(lat=22, lon=33, timestamp=Timer.current_time_ms())
        self.on_ready_event.trigger()

    def on_enter_sleep(self, event):
        # cancel any running timer and clear the last location
        # pretend to sleep
        self.gps_timer.cancel()
        self._last_location = None


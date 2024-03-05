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
        Transition('gps_timeout', after='on_timeout'),
        Transition('sleep', None, 'sleep'),

    ]

    def __init__(self, gps_timeout_ms=15000, on_ready_event=None, on_fail_event=None, timer=None, baudrate=9600, tx=8,
                 rx=7, **kwargs):
        super(MPYGPS, self).__init__(states=self.states, transitions=self.transitions, **kwargs)
        self.gps_timeout_ms = gps_timeout_ms
        self.on_ready_event = on_ready_event
        self.on_fail_event = on_fail_event
        # self.check_gps_timer = timer if timer else Timer(event=self.get_event('check_gps'), duration_ms= 3000, recurring=True)
        self.check_gps_timer = Timer(event=self.get_event('check_gps'), duration_ms=3000, recurring=True)
        self.gps_timeout = Timer(event=self.get_event('gps_timeout'), duration_ms=gps_timeout_ms, recurring=False)
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
        self.check_gps_timer.reset()
        self.gps_timeout.reset()
        print("Enter Locating")

    def on_check_gps(self, event):
        # After event check_gps which is executed by timer
        # Check for fix: If fix, update location and trigger gps_ready

        msg_bytes = self.uart.readline()

        #         if msg_bytes == None or msg_bytes[1:6] != b'GPRMC':
        #             print("No fix: " + str(msg_bytes))
        #             self._last_location = None
        #         else
        #             msg_str = msg_bytes.decode().strip()
        #             msg = nmea.parse_sentence(msg_str)
        #
        #             if msg['fix_quality'] == 1:
        #                 print("GPRMC Sentence: " + str(msg_bytes))
        #                 self._last_location=msg
        #                 self.get_event('gps_ready').trigger()
        #             else:
        #                 print("No fix: " + str(msg_bytes))
        #                 self._last_location = None

        if msg_bytes is not None:
            if msg_bytes[1:6] == b'GPRMC':

                msg_str = msg_bytes.decode().strip()
                msg = nmea.parse_sentence(msg_str)

                if msg['fix_quality'] == 1:
                    print("GPRMC Sentence: " + str(msg_bytes))
                    self._last_location = msg
                    self.get_event('gps_ready').trigger()
                else:
                    # print("No fix: " + str(msg_bytes))
                    self._last_location = None
        else:
            # print("No fix: " + str(msg_bytes))
            self._last_location = None

    def on_timeout(self, event):
        # Cancel timers and callback that it failed
        self.check_gps_timer.cancel()
        self.gps_timeout.cancel()
        self.on_fail_event.trigger()

    def on_enter_ready(self, event):
        # If we have a fix, log message
        self.check_gps_timer.cancel()
        self.gps_timeout.cancel()
        print("GPS READY")
        self.on_ready_event.trigger()

    def on_enter_sleep(self, event):
        # cancel any running timer and clear the last location
        # pretend to sleep
        self.check_gps_timer.cancel()
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
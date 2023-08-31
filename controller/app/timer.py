import time


class Timer(object):
    active_timers = set()

    def __init__(self, event=None, duration_ms=0, recurring=False):
        self._deadline = 0
        self.duration_ms = duration_ms
        self.recurring = recurring
        self.event = event
        self.active = False

    @classmethod
    def check_active_timers(cls):
        timers = [t for t in cls.active_timers]
        for t in timers:
            t.check()

    @classmethod
    def get_next_timer(cls):
        return min(cls.active_timers, key=lambda x: x._deadline) if cls.active_timers else None

    @classmethod
    def cancel_all(cls):
        timers = [t for t in cls.active_timers]
        for t in timers:
            t.cancel()

    @staticmethod
    def current_time_ms():
        return time.time_ns() // 1000000

    def is_expired(self):
        return Timer.current_time_ms() >= self._deadline if self.active else False

    def check(self):
        if self.is_expired():
            self.trigger_event()
            if self.recurring:
                self.reset()
            else:
                self.cancel()

    def time_remaining_ms(self):
        return self._deadline - self.current_time_ms() if self.active else 0

    def reset(self, duration_ms=None, recurring=None, event=None):
        if duration_ms is not None:
            self.duration_ms = duration_ms
        if recurring is not None:
            self.recurring = recurring
        if event is not None:
            self.event = event
        self._deadline = Timer.current_time_ms() + self.duration_ms
        self.active = True
        self.active_timers.add(self)

    def cancel(self):
        self.active = False
        self.active_timers.discard(self)

    def trigger_event(self):
        if self.event:
            self.event.trigger()

    def save_state(self):
        return dict(
            active=self.active,
            deadline=self._deadline
        )

    def load_state(self, state):
        self.active = state['active']
        self._deadline = state['deadline']
        if self.active:
            self.active_timers.add(self)

class MockTime(object):
    # can't use unittest.mock in micropython, so we are manually mocking Timer.current_time_ms() to return the
    # value defined in this class so a test can control what time the Timer class sees

    def __new__(cls):
        # Make this a singleton class
        if not hasattr(cls, 'instance'):
            cls.instance = super(MockTime, cls).__new__(cls)
        return cls.instance

    time_ms = 0

    def __init__(self):
        self.old_time_fn = None

    def current_time_ms(self):
        return self.time_ms

    def set_current_time_ms(self, value):
        self.time_ms = value
        return value

    def increment_time_ms(self, increment):
        self.time_ms += increment
        return self.time_ms

    def setup(self):
        self.time_ms = 0
        self.old_time_fn = Timer.current_time_ms
        Timer.current_time_ms = self.current_time_ms

    def tearDown(self):
        Timer.current_time_ms = self.old_time_fn

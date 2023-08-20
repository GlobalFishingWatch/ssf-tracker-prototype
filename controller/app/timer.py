import time


class Timer(object):
    active_timers = set()

    def __init__(self, event=None, duration_ms=0, recurring=False):
        self._deadline = 0
        self.duration_ms = duration_ms
        self.recurring = recurring
        self.event = event
        self.active = False

    @staticmethod
    def current_time_ms():
        return time.time_ns() // 1000000

    def is_expired(self):
        return self.current_time_ms() >= self._deadline if self.active else False

    def check(self):
        if self.is_expired():
            self.trigger_event()
            if self.recurring:
                self.reset()
            else:
                self.cancel()

    @classmethod
    def check_active_timers(cls):
        timers = [t for t in cls.active_timers]
        for t in timers:
            t.check()

    def reset(self, duration_ms=None, recurring=None, event=None):
        if duration_ms is not None:
            self.duration_ms = duration_ms
        if recurring is not None:
            self.recurring = recurring
        if event is not None:
            self.event = event
        self._deadline = self.current_time_ms() + self.duration_ms
        self.active = True
        self.active_timers.add(self)

    def cancel(self):
        self.active = False
        self.active_timers.discard(self)

    def trigger_event(self):
        if self.event:
            self.event.trigger()


# A subclass of timer that lets us manually set the current time, used for testing
class ManualTimer(Timer):
    def __init__(self, **kwargs):
        self.time_ms = 0
        super(ManualTimer, self).__init__(**kwargs)

    def current_time_ms(self):
        return self.time_ms

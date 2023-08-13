import time

class Timer(object):
    active_timers = set()

    def __init__(self, event_data=None, event='timeout', duration_ms=0, recurring=False):
        self._deadline = 0
        self.duration_ms = duration_ms
        self.recurring = recurring
        self.event = event
        self.event_data = event_data
        self.active = False

    def _get_time_ms(self):
        return time.time() * 1000

    def is_expired(self):
        return self._get_time_ms() >= self._deadline if self.active else False

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

    def reset(self, duration_ms=None, recurring=None, event=None, event_data=None):
        if duration_ms is not None: self.duration_ms = duration_ms
        if recurring is not None: self.recurring = recurring
        if event is not None: self.event = event
        if event_data is not None: self.event_data = event_data
        self._deadline = self._get_time_ms() + self.duration_ms
        self.active = True
        self.active_timers.add(self)

    def cancel(self):
        self.active = False
        self.active_timers.remove(self)


    def trigger_event(self):
        if self.event_data and self.event_data.machine:
            self.event_data.machine.trigger_event(trigger=self.event, event_data=self.event_data)

import unittest

from app.timer import Timer


class ManualTimer(Timer):
    def __init__(self, **kwargs):
        self.time_ms = 0
        super(ManualTimer, self).__init__(**kwargs)

    def _get_time_ms(self):
        return self.time_ms

class MockStateMachine(object):
    def __init__(self):
        self.event_count = 0

    def trigger_event(self, trigger, event_data):
        self.event_count += 1

class MockEventData(object):
    def __init__(self, machine):
        self.machine = machine

class TestTimer(unittest.TestCase):
    def setUp(self):
        pass

    def test_is_expired(self):
        t = ManualTimer()
        self.assertFalse(t.is_expired())
        t._deadline = 100
        t.time_ms = 101
        self.assertFalse(t.is_expired())
        t.active = True
        self.assertTrue(t.is_expired())

    def test_reset(self):
        t = ManualTimer()
        t.reset(duration_ms=100)
        self.assertEqual(t._deadline, 100)

    def test_trigger_event(self):
        machine = MockStateMachine()
        event_data = MockEventData(machine=machine)
        t = ManualTimer(event_data=event_data)
        t.trigger_event()
        self.assertEqual(machine.event_count, 1)

    def test_check(self):
        machine = MockStateMachine()
        event_data = MockEventData(machine=machine)
        t = ManualTimer(event_data=event_data)
        t.reset(duration_ms=100)
        self.assertFalse(t.is_expired())
        t.check()
        self.assertEqual(machine.event_count, 0)
        t.time_ms = 100
        self.assertTrue(t.is_expired())
        t.check()
        self.assertEqual(machine.event_count, 1)

    def test_active_timers(self):
        Timer.active_timers = set()
        t = ManualTimer()
        t.reset(duration_ms=100)
        self.assertIn(t, Timer.active_timers)
        t.cancel()
        self.assertNotIn(t, Timer.active_timers)
        self.assertEqual(len(Timer.active_timers), 0)



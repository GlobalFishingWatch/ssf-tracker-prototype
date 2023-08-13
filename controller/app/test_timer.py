import unittest

from timer import Timer
from timer import ManualTimer


class MockEvent(object):
    def __init__(self):
        self.trigger_count = 0

    def trigger(self):
        self.trigger_count += 1


class TestTimer(unittest.TestCase):

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
        event = MockEvent()
        t = ManualTimer(event=event)
        t.trigger_event()
        self.assertEqual(event.trigger_count, 1)

    def test_check(self):
        event = MockEvent()
        t = ManualTimer(event=event)
        t.reset(duration_ms=100)
        self.assertFalse(t.is_expired())
        t.check()
        self.assertEqual(event.trigger_count, 0)
        t.time_ms = 100
        self.assertTrue(t.is_expired())
        t.check()
        self.assertEqual(event.trigger_count, 1)

    def test_active_timers(self):
        Timer.active_timers = set()
        t = ManualTimer()
        t.reset(duration_ms=100)
        self.assertIn(t, Timer.active_timers)
        t.cancel()
        self.assertTrue(t not in Timer.active_timers)
        self.assertEqual(len(Timer.active_timers), 0)

    def test_cancel_inactive(self):
        t = ManualTimer()
        t.cancel()

if __name__ == '__main__':
    unittest.main()
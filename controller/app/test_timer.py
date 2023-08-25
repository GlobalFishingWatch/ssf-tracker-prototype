import unittest

from timer import Timer
from timer import MockTime
from statemachine import MockEvent
from statemachine import Event


class TestTimer(unittest.TestCase):
    # can't use unittest.mock in micropython, so we are manually mocking Timer.current_time_ms() to return the
    # value defined in this class so the test can control what time the Timer class sees
    # time_ms = 0
    #
    # @staticmethod
    # def current_time_ms():
    #     return TestTimer.time_ms

    def setUp(self):
        self.mock_time = MockTime()
        self.mock_time.setup()

    def tearDown(self):
        self.mock_time.tearDown()

    # def setUp(self):
    #     TestTimer.time_ms = 0
    #     self.old_current_time_ms = Timer.current_time_ms
    #     Timer.current_time_ms = TestTimer.current_time_ms
    #
    # def tearDown(self):
    #     Timer.current_time_ms = self.old_current_time_ms

    def test_is_expired(self):
        t = Timer()
        self.assertFalse(t.is_expired())
        t._deadline = 100
        self.mock_time.set_current_time_ms(101)
        self.assertFalse(t.is_expired())
        t.active = True
        self.assertTrue(t.is_expired())

    def test_reset(self):
        t = Timer()
        t.reset(duration_ms=100)
        self.assertEqual(t._deadline, 100)

    def test_trigger_event(self):
        event = MockEvent('timeout')
        t = Timer(event=event)
        t.trigger_event()
        Event.trigger_scheduled_events()
        self.assertEqual(event.trigger_count, 1)

    def test_check(self):
        event = MockEvent('timeout')
        t = Timer(event=event)
        t.reset(duration_ms=100)
        self.assertFalse(t.is_expired())
        t.check()
        Event.trigger_scheduled_events()
        self.assertEqual(event.trigger_count, 0)
        self.mock_time.increment_time_ms(100)
        self.assertTrue(t.is_expired())
        t.check()
        Event.trigger_scheduled_events()
        self.assertEqual(event.trigger_count, 1)

    def test_active_timers(self):
        Timer.active_timers = set()
        t = Timer()
        t.reset(duration_ms=100)
        self.assertIn(t, Timer.active_timers)
        t.cancel()
        self.assertTrue(t not in Timer.active_timers)
        self.assertEqual(len(Timer.active_timers), 0)

    def test_cancel_inactive(self):
        t = Timer()
        t.cancel()


if __name__ == '__main__':
    unittest.main()

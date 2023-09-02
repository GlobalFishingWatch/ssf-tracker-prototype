import unittest

from timer import Timer
from timer import MockTime
from statemachine import MockEvent
from statemachine import Event
import ujson as json

class TestTimer(unittest.TestCase):

    def setUp(self):
        self.mock_time = MockTime()
        self.mock_time.setup()

    def tearDown(self):
        self.mock_time.tearDown()

    def test_is_expired(self):
        t = Timer()
        self.assertFalse(t.is_expired())
        t._deadline = 100
        self.mock_time.set_current_time_ms(101)
        self.assertFalse(t.is_expired())
        t.active = True
        self.assertTrue(t.is_expired())

    def test_time_remaining(self):
        t = Timer()
        self.assertEqual(t.time_remaining_ms(), 0)
        t._deadline = 100
        self.assertEqual(t.time_remaining_ms(), 0)
        t.active = True
        self.assertEqual(t.time_remaining_ms(), 100)

    def test_get_next_timer(self):
        Timer.active_timers = set()
        self.assertIsNone(Timer.get_next_timer())
        t1 = Timer()
        t1.reset(duration_ms=100)
        self.assertIs(Timer.get_next_timer(), t1)
        t2 = Timer()
        t2.reset(duration_ms=50)
        self.assertIs(Timer.get_next_timer(), t2)

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

    def test_cancel(self):
        t = Timer()
        t.reset(duration_ms=100)
        self.assertTrue(t.active)
        self.assertNotEqual(t._deadline,  0)
        t.cancel()
        self.assertFalse(t.active)
        self.assertEqual(t._deadline,  0)

    def test_cancel_inactive(self):
        t = Timer()
        t.cancel()
        self.assertFalse(t.active)

    def test_cancel_all(self):
        t = Timer()
        t.reset(duration_ms=100)
        self.assertIn(t, Timer.active_timers)
        Timer.cancel_all()
        self.assertEqual(len(Timer.active_timers), 0)

    def test_save_state(self):
        t = Timer()
        self.assertEqual(t.save_state(), {'active': False, 'deadline': 0})

    def test_load_state(self):
        t = Timer()
        state = {'active': True, 'deadline': 100}
        t.load_state(state)
        self.assertEqual(t._deadline, state['deadline'])
        self.assertTrue(t.active)
        self.assertIn(t, Timer.active_timers)

    def test_state_to_json(self):
        t = Timer()
        t._deadline = 123
        t.load_state(json.loads(json.dumps(t.save_state())))
        self.assertEqual(t._deadline, 123)

if __name__ == '__main__':
    unittest.main()

import unittest

from gps import MockGPS
from timer import MockTime
from timer import Timer
from statemachine import MockEvent
from statemachine import Event


class TestMockGPS(unittest.TestCase):

    def setUp(self):
        self.mock_time = MockTime()
        self.mock_time.setup()

    def tearDown(self):
        self.mock_time.tearDown()

    def test_main_sequence(self):
        event = MockEvent('gps_ready')
        machine = MockGPS(name='gps', on_ready_event=event)
        self.assertIsNone(machine.last_location)

        # start the gos trying to fix a location
        machine.trigger_event(machine.get_event('locate'))
        self.assertIsNone(machine.last_location)
        self.assertTrue(machine.gps_timer.active)

        # simulate time passing
        self.mock_time.increment_time_ms(machine.gps_timeout_ms)
        Timer.check_active_timers()
        Event.trigger_scheduled_events()

        # The timer should have fired and put us into the ready state
        self.assertEqual(machine.state.name, 'ready')
        self.assertIsNotNone(machine.last_location)
        self.assertEqual(event.trigger_count, 1)

        machine.trigger_event(machine.get_event('sleep'))
        self.assertIsNone(machine.last_location)


if __name__ == '__main__':
    unittest.main()

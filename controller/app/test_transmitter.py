import unittest

from transmitter import MockTransmitter
from timer import MockTime
from timer import Timer
from statemachine import MockEvent
from statemachine import Event


class TestMockTransmitter(unittest.TestCase):

    def setUp(self):
        self.mock_time = MockTime()
        self.mock_time.setup()

    def tearDown(self):
        self.mock_time.tearDown()

    def test_main_sequence(self):
        event = MockEvent('transmit_success')
        machine = MockTransmitter(name='transmitter', on_success_event=event)
        message = 'foo'
        self.assertIsNone(machine._message)

        # start the transmitter trying to send a message
        machine.trigger_event(machine.get_event('transmit', message=message))
        self.assertEqual(machine._message, message)
        self.assertTrue(machine.transmit_timer.active)

        # simulate time passing
        self.mock_time.increment_time_ms(machine.timeout_ms)
        Timer.check_active_timers()
        Event.trigger_scheduled_events()

        # The timer should have fired and put us into the ready state
        self.assertEqual(machine.state.name, 'sleep')
        self.assertEqual(event.trigger_count, 1)



if __name__ == '__main__':
    unittest.main()

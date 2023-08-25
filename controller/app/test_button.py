import unittest

from button import Button
# from timer import Timer
from timer import MockTime
from statemachine import MockEvent
from statemachine import Event


class TestButton(unittest.TestCase):

    def setUp(self):
        self.mock_time = MockTime()
        self.mock_time.setup()

    def tearDown(self):
        self.mock_time.tearDown()

    def test_button_transitions(self):
        button = Button(on_press_event=MockEvent('press'),
                        on_release_event=MockEvent('release'))
        self.assertEqual(button.state.name, 'released')
        button.trigger_event('btn_down')
        self.assertEqual(button.state.name, 'pressing')
        button.trigger_event('btn_down')
        self.assertEqual(button.state.name, 'pressing')
        button.trigger_event('btn_up')
        self.assertEqual(button.state.name, 'released')
        self.assertEqual(button.on_release_event.trigger_count, 0)
        button.trigger_event('btn_down')
        button.trigger_event('timeout')
        self.assertEqual(button.state.name, 'pressed')
        self.assertEqual(button.on_press_event.trigger_count, 1)
        button.trigger_event('btn_up')
        button.trigger_event('timeout')
        self.assertEqual(button.on_release_event.trigger_count, 1)

    def test_button_timing(self):
        button = Button(on_press_event=MockEvent('press'),
                        on_release_event=MockEvent('release'))

        button.trigger_event('btn_down')
        self.mock_time.increment_time_ms(button.bounce_timeout_ms)
        button.bounce_timer.check()
        Event.trigger_scheduled_events()
        self.assertEqual(button.state.name, 'pressed')
        self.assertEqual(button.on_press_event.trigger_count, 1)


if __name__ == '__main__':
    unittest.main()

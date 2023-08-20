import unittest

from button import Button
from timer import ManualTimer
from statemachine import Event

class MockEvent(object):
    def __init__(self):
        self.trigger_count = 0

    def trigger(self):
        self.trigger_count += 1


class TestButton(unittest.TestCase):
    def test_button_transitions(self):
        button = Button(on_press_event=MockEvent(),
                        on_release_event=MockEvent())
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
        button = Button(on_press_event=MockEvent(),
                        on_release_event=MockEvent())
        button.bounce_timer=ManualTimer(event=button.get_event('timeout'))
        button.trigger_event('btn_down')
        button.bounce_timer.time_ms += button.bounce_timeout_ms
        button.bounce_timer.check()
        self.assertEqual(button.state.name, 'pressed')
        self.assertEqual(button.on_press_event.trigger_count, 1)


if __name__ == '__main__':
    unittest.main()

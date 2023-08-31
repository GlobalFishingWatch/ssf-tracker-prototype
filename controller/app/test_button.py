import unittest

from button import Button
from timer import MockTime
from statemachine import MockEvent
from statemachine import Event
from statemachine import StateMachine
from test_statemachine import EventTestRunner

class TestButton(EventTestRunner):

    def setUp(self):
        self.mock_time = MockTime()
        self.mock_time.setup()
        self.button = Button(name='Button1',
                             on_press_event=MockEvent('press'),
                             on_release_event=MockEvent('release'))

    def tearDown(self):
        self.mock_time.tearDown()
        StateMachine.machines = {}


    def test_button_transitions(self):
        self.assertEqual(self.button.state.name, 'released')
        events = [
            ('Button1', 'btn_down', 100, 'pressing'),
            ('Button1', 'btn_down', 1, 'pressing'),
            ('Button1', 'btn_up', 1, 'released'),
            ('Button1', 'btn_down', 1, 'pressing'),
            ('Button1', 'timeout', 10, 'pressed'),
        ]
        self.run_events(events)
        self.assertEqual(self.button.on_press_event.trigger_count, 1)
        events = [
            ('Button1', 'btn_up', 100, 'releasing'),
            ('Button1', 'timeout', 10, 'released'),
        ]
        self.run_events(events)


    def test_save_state(self):
        self.assertEqual(self.button.save_state(), {'state': 'released',
                                                 'timer': {'active': False, 'deadline': 0}
                                                    })

    def test_load_state(self):
        state = {'state': 'pressing',
                 'timer': {'active': True, 'deadline': 10}
                 }
        self.button.load_state(state)
        self.assertEqual(self.button.state.name, 'pressing')
        self.assertEqual(self.button.bounce_timer.active, True)

    def test_button_timing(self):
        self.button.trigger_event('btn_down')
        self.mock_time.increment_time_ms(self.button.bounce_timeout_ms)
        self.button.bounce_timer.check()
        Event.trigger_scheduled_events()
        self.assertEqual(self.button.state.name, 'pressed')
        self.assertEqual(self.button.on_press_event.trigger_count, 1)


if __name__ == '__main__':
    unittest.main()

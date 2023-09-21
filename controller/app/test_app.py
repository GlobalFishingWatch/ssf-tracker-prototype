import unittest
from copy import deepcopy
from app import App
from config import default_app_state
from wiring import MockWiring
from statemachine import StateMachine
from statemachine import MockEvent
from timer import MockTime
from timer import Timer
from test_statemachine import EventTestRunner

class TestApp(unittest.TestCase):
    def setUp(self):
        self.config = {
            'MIN_LIGHTSLEEP_TIME_MS': 10,
            'MAX_LIGHTSLEEP_TIME_MS': 100,
            'MIN_DEEPSLEEP_TIME_MS': 10,
            'MAX_DEEPSLEEP_TIME_MS': 100,
            'LOG_LEVEL': 'INFO'
        }
        self.app = App.from_settings(self.config, wiring_type=MockWiring)
        self.app.initialize()

    def tearDown(self):
        StateMachine.machines = {}

    def test_app_creation(self):
        self.assertEqual(self.app.state.name, 'boot')

    def test_is_running(self):
        self.assertTrue(self.app.is_running())

    def test_lightsleep(self):
        # no timers set, so should sleep for the max time
        Timer.cancel_all()
        self.app.lightsleep()
        self.assertEqual(self.app.wiring.cumulative_lightsleep_time_ms, self.config['MAX_LIGHTSLEEP_TIME_MS'])

        # set a timer with a very short deadline - now we should not sleep
        t = Timer()
        t.reset(duration_ms=1)
        before = self.app.wiring.cumulative_lightsleep_time_ms
        self.app.lightsleep()
        self.assertEqual(self.app.wiring.cumulative_lightsleep_time_ms, before)

    def test_save_state(self):
        self.assertEqual(self.app.save_state(), default_app_state)

    def test_load_state(self):
        state = deepcopy(default_app_state)
        state['state'] = 'locating'
        state['button1']['state'] = 'pressed'
        state['gps_timer']['active'] = True

        self.app.load_state(state)
        self.assertEqual(self.app.state.name, 'locating')
        self.assertEqual(self.app.gps_timer.active, True)
        self.assertEqual(self.app.button1.state.name, 'pressed')

    # TODO test self.app.run()

    def test_max_sleep_time_ms(self):
        Timer.cancel_all()
        self.assertEqual(self.app.max_sleep_time_ms(1000), 1000)
        t = Timer(duration_ms=99)
        t.reset()
        self.assertLessEqual(self.app.max_sleep_time_ms(1000), 99)

    def test_can_deep_sleep(self):
        Timer.cancel_all()
        self.assertTrue(self.app.can_deep_sleep(event=None))
        t = Timer(duration_ms=self.config['MIN_DEEPSLEEP_TIME_MS'] / 2)
        t.reset()
        self.assertFalse(self.app.can_deep_sleep(event=None))

    def test_on_sleep(self):
        Timer.cancel_all()
        self.app.on_sleep(MockEvent('mock'))
        max_time = self.app.config['MAX_DEEPSLEEP_TIME_MS']
        self.assertEqual(self.app.wiring.cumulative_deepsleep_time_ms, max_time)

    def test_wake_from_sleep(self):
        self.app.wiring.deepsleep(1)
        self.app.initialize()


    def test_app_btn_down(self):
        self.assertEqual(self.app.wiring.led1, 0)
        self.app.wiring.btn1 = 1    # button down
        self.app.tick()
        self.app.button1.bounce_timer.trigger_event()   # bounce timeout
        self.app.tick()
        self.assertEqual(self.app.wiring.led1, 1)
        self.app.wiring.btn1 = 0    # button up
        self.app.tick()
        self.app.button1.bounce_timer.trigger_event()   # bounce timeout
        self.app.tick()
        self.assertEqual(self.app.wiring.led1, 0)

    def test_app_locating(self):
        self.assertEqual(self.app.wiring.gps_enable, 0)
        self.app.tick()
        self.app.trigger_event('gps_timer')
        self.app.tick()
        self.assertEqual(self.app.wiring.gps_enable, 1)
        self.assertTrue(self.app.wiring.gps_timer.active)
        self.assertEqual(self.app.wiring.gps_timer.event.name, 'gps_ready')
        self.app.trigger_event('gps_ready')
        self.app.tick()
        self.assertEqual(self.app.wiring.gps_enable, 0)
        self.assertEqual(len(self.app.locations), 1)



class TestAppTransitions(EventTestRunner):
    def setUp(self):
        self.config = {
            'LOG_LEVEL': 'INFO'
        }
        self.app = App.from_settings(name='TestApp', settings=self.config, wiring_type=MockWiring)
        self.app.initialize()

    def tearDown(self):
        StateMachine.machines = {}

    def test_transitions(self):
        self.assertEqual(self.app.state.name, 'boot')
        events = [
            ('TestApp', None, 0, 'idle'),     # transition from boot to idle happens immediately
            ('TestApp', 'idle_timeout', 0, 'sleep'),  # advance the timer to trigger event 'idle_timeout'
            ('TestApp', 'timer_wake', 0, 'idle'),
            ('TestApp', 'gps_timer', 0, 'locating'),
            ('TestApp', None, MockWiring.MOCK_TIME_TO_FIX_MS, None),
            ('TestApp', None, 0, 'idle'),
            ('TestApp', 'gps_timer', 0, 'locating'),
            ('TestApp', 'gps_timeout', 0, 'idle'),
        ]
        self.run_events(events)


if __name__ == '__main__':
    unittest.main()

import unittest
from app import App
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
        expected = {
            'state': 'boot',
            'idle_timer': {'active': False, 'deadline': 0},
            'button1': {'state': 'released', 'timer': {'active': False, 'deadline': 0},}
        }
        self.assertEqual(self.app.save_state(), expected)

    def test_load_state(self):
        state = {
            'state': 'sleep',
            'idle_timer': {'active': True, 'deadline': 1000},
            'button1': {'state': 'released', 'timer': {'active': False, 'deadline': 0},}
        }
        self.app.load_state(state)
        self.assertEqual(self.app.state.name, 'sleep')
        self.assertEqual(self.app.idle_timer.active, True)
        self.assertEqual(self.app.button1.state.name, 'released')

    # TODO test self.app.run()

    def test_get_sleep_time(self):
        Timer.cancel_all()
        min_time = self.app.config['MIN_DEEPSLEEP_TIME_MS']
        max_time = self.app.config['MAX_DEEPSLEEP_TIME_MS']
        sleep_time = self.app.get_sleep_time_ms(min_time, max_time)
        self.assertEqual(sleep_time, max_time)
        timer = Timer()
        timer.reset(duration_ms=min_time)
        sleep_time = self.app.get_sleep_time_ms(min_time, max_time)
        self.assertEqual(sleep_time, 0)
        timer.reset(duration_ms=min_time+10)
        sleep_time = self.app.get_sleep_time_ms(min_time, max_time)
        self.assertEqual(sleep_time, min_time+10)

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
            ('MockGPS1', None, 0, 'sleep'),  # gps should be sleeping
            ('TestApp', 'gps_timer', 0, 'locating'),
            ('MockGPS1', None, 0, 'locating'),  # gps should now be active
            ('MockGPS1', 'gps_ready', 0, 'sleep'),  # gps should now be active
        ]
        self.run_events(events)


if __name__ == '__main__':
    unittest.main()

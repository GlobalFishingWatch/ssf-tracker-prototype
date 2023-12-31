import unittest
from wiring import MockWiring
from statemachine import MockEvent

class TestWiring(unittest.TestCase):

    def setUp(self):
        config = {}
        self.wiring = MockWiring(config=config,
                                 btn1_up_event=MockEvent('btn_up'),
                                 btn1_down_event=MockEvent('btn_down'),
                                 gps_fix_event=MockEvent('gps_ready'))
        self.wiring.initialize()

    def test_wiring(self):
        self.assertEqual(self.wiring.btn1, 0)
        self.assertEqual(self.wiring.led1, 0)
        self.wiring.led1 = 1
        self.assertEqual(self.wiring.led1, 1)

    def test_events(self):
        self.assertEqual(self.wiring.btn_down_event.trigger_count, 0)
        self.assertEqual(self.wiring.btn1, 0)
        self.wiring.btn1 = 1    # trigger btn_down
        self.assertEqual(self.wiring.btn_down_event.trigger_count, 1)

    def test_sleep(self):
        self.wiring.lightsleep(time_ms=10)

    def test_gps(self):
        self.wiring.gps_wake()
        self.assertEqual(self.wiring._gps_enable.value(), 1)
        self.assertEqual(self.wiring.gps_fix_event.kwargs, MockWiring.MOCK_LOCATION)
        self.wiring.gps_sleep()
        self.assertEqual(self.wiring._gps_enable.value(), 0)

if __name__ == '__main__':
    unittest.main()

import unittest
from wiring import MockWiring
from statemachine import MockEvent


class TestWiring(unittest.TestCase):

    def setUp(self):
        config = {}
        self.wiring = MockWiring(config, btn1_up_event=MockEvent(), btn1_down_event=MockEvent())
        self.wiring.initialize()

    def test_wiring(self):
        self.assertEqual(self.wiring.btn1, 1)
        self.assertEqual(self.wiring.led1, 0)
        self.wiring.led1 = 1
        self.assertEqual(self.wiring.led1, 1)

    def test_events(self):
        self.assertEqual(self.wiring.btn_down_event.trigger_count, 0)
        self.assertEqual(self.wiring.btn1, 1)
        self.wiring.btn1 = 0    # trigger btn_down
        self.assertEqual(self.wiring.btn_down_event.trigger_count, 1)

    def test_sleep(self):
        self.wiring.lightsleep(time_ms=10)


if __name__ == '__main__':
    unittest.main()

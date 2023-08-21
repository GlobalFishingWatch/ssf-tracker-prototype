import unittest
from wiring_esp32 import WiringESP32
from statemachine import MockEvent


class TestWiringEsp32(unittest.TestCase):
    def setUp(self):
        config = {}
        self.wiring = WiringESP32(config, btn1_up_event=MockEvent(), btn1_down_event=MockEvent())
        self.wiring.initialize()

    def test_wiring(self):
        self.assertEqual(self.wiring.btn1, 1)
        self.assertEqual(self.wiring.led1, 0)
        self.wiring.led1 = 1
        self.assertEqual(self.wiring.led1, 1)

    def test_sleep(self):
        self.wiring.lightsleep(time_ms=10)


if __name__ == '__main__':
    unittest.main()

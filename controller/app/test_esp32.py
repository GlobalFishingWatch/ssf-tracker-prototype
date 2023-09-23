import unittest
from wiring_esp32 import WiringESP32
from statemachine import MockEvent


class TestWiringEsp32(unittest.TestCase):
    def setUp(self):
        config = {}
        self.wiring = WiringESP32(config=config, btn1_up_event=MockEvent('btn_up'),
                                          btn1_down_event=MockEvent('btn_down'),
                                          gps_fix_event=MockEvent('gps_ready'))
        self.wiring.initialize()

    def test_wiring(self):
        self.assertEqual(self.wiring.btn1, 0)
        self.assertEqual(self.wiring.led1, 0)
        self.assertEqual(self.wiring.rgb, 'off')
        self.wiring.led1 = 1
        self.assertEqual(self.wiring.led1, 1)
        self.wiring.rgb = 'red'
        self.assertEqual(self.wiring.rgb, 'red')

    # def test_sleep(self):
    #     self.wiring.lightsleep(time_ms=10)


if __name__ == '__main__':
    unittest.main()

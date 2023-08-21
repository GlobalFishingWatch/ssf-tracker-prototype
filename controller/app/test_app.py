import unittest
from app import App
from wiring import MockWiring

class TestApp(unittest.TestCase):
    def setUp(self):
        config = {}
        self.app = App(WiringType=MockWiring, config=config)
        self.app.initialize()

    def test_app_creation(self):
        self.assertEqual(self.app.state.name, 'setup')

    # def test_app_run(self):
    #     self.app.run()

    def test_app_btn_down(self):
        self.assertEqual(self.app.wiring.led1, 0)
        self.app.wiring.btn1 = 0    # button down
        self.app.button1.bounce_timer.trigger_event()   # bounce timeout
        self.assertEqual(self.app.wiring.led1, 1)
        self.app.wiring.btn1 = 1    # button up
        self.app.button1.bounce_timer.trigger_event()   # bounce timeout
        self.assertEqual(self.app.wiring.led1, 0)

if __name__ == '__main__':
    unittest.main()
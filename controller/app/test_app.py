import unittest
from app import App
from wiring import MockWiring
from statemachine import Event

class TestApp(unittest.TestCase):
    def setUp(self):
        config = {}
        self.app = App(WiringType=MockWiring, config=config)
        self.app.initialize()

    def test_app_creation(self):
        self.assertEqual(self.app.state.name, 'boot')

    def test_app_tick(self):
        self.app.tick()

    # def test_app_run(self):
    #     self.app.run()

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


if __name__ == '__main__':
    unittest.main()

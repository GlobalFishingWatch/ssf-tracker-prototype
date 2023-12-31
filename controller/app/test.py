# test.py
# Run the full unit test suite
#
# Usage:
# Python cli in osx
#
#   $ python test.py
#
# Micropython cli in osx
#
#   $ micropython test.py
#
# Micropython REPL running in the esp32 device
#
#   >>> import test
#   >>> test.run_all_tests_esp32()


import unittest


# All these imported tests will be run when unittest.main() is invoked below
# Note that TestWiringEsp32 is not included here because it can only be tested
# when running on the device
from test_app import TestApp, TestAppTransitions
from test_button import TestButton
from test_util import TestUtil
from test_statemachine import TestStateMachine
from test_timer import TestTimer
from test_wiring import TestWiring
# from test_gps import TestMockGPS
from test_transmitter import TestMockTransmitter
from test_nmea import TestNMEA


def run_all_tests_esp32():
    suite = unittest.TestSuite()
    suite.addTest(TestApp())
    suite.addTest(TestAppTransitions())
    suite.addTest(TestButton())
    suite.addTest(TestUtil())
    suite.addTest(TestStateMachine())
    suite.addTest(TestTimer())
    suite.addTest(TestWiring())
    # suite.addTest(TestMockGPS())
    suite.addTest(TestMockTransmitter())
    suite.addTest(TestNMEA())

    # include tests that will only run on the ESP32
    from test_esp32 import TestWiringEsp32
    suite.addTest(TestWiringEsp32())

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    unittest.main()

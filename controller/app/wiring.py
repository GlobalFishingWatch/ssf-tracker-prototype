# Model class for the hardware interface
# This class provides stub implementations that do not depend on
# hardware specific modules available in micropython, so it cann be used
# for testing outside the device (like on the development machine or in continuous integration)

# for testing outside the device, use MockWiring
# For use on the device, you should use a hardware specific subclass of Wiring

import time
from timer import Timer


class Wiring(object):
    """
    Abstract base class that provides an interface to the device hardware.   You must create a subclass
    that implements initialize().  Use MockWiring for a non-functional test interface or use a hardware
    specific subclass
    """
    def __init__(self, config,
                 btn1_up_event=None,
                 btn1_down_event=None,
                 gps_fix_event=None):
        self.config = config
        self.btn_up_event = btn1_up_event
        self.btn_down_event = btn1_down_event
        self.gps_fix_event = gps_fix_event
        self._led1 = None
        self._rgb = None
        self._btn1 = None
        self._gps_enable = None
        self._wake_reason = 'RESET'

    def initialize(self):
        raise NotImplementedError('You must create a subclass of Wiring that implements initialize()')

    @property
    def led1(self):
        return self._led1.value()

    @led1.setter
    def led1(self, value):
        self._led1.value(value)

    @property
    def rgb(self):
        return self._rgb.value()

    @rgb.setter
    def rgb(self, value):
        self._rgb.value(value)

    @property
    def btn1(self):
        return self._btn1.value()

    @property
    def gps_enable(self):
        return self._gps_enable.value()

    @gps_enable.setter
    def gps_enable(self, value):
        self._gps_enable.value(value)

    def trigger_event(self, event):
        if event:
            event.trigger()

    def lightsleep(self, time_ms):
        if hasattr(time, 'sleep_ms'):
            time.sleep_ms(time_ms)
        else:
            time.sleep(time_ms / 1000)

    def deepsleep(self, time_ms):
        self.lightsleep(time_ms)

    def reset(self):
        self._wake_reason = 'RESET'

    def wake_reason(self):
        return self._wake_reason

    def gps_wake(self):
        self._gps_enable.value(1)

    def gps_sleep(self):
        self._gps_enable.value(0)

    def gps_update(self):
        pass


class MockWiring(Wiring):
    """
    Non-functional implementation of Wiring for use in unit testing
    """

    MOCK_LOCATION = {'lat': 39, 'lon': -80, 'utc_seconds': 12345678}
    MOCK_TIME_TO_FIX_MS = 2000

    def __init__(self, **kwargs):
        self.cumulative_lightsleep_time_ms = 0
        self.cumulative_deepsleep_time_ms = 0
        super(MockWiring, self).__init__(**kwargs)
        self.gps_timer = None

    class MockPin(object):
        def __init__(self, value=0, irq_handler=None):
            self._value = value
            self.irq_handler = irq_handler

        def value(self, new_value=None):
            if new_value is not None:
                old_value = self._value
                self._value = new_value
                if (old_value != new_value) and self.irq_handler is not None:
                    self.irq_handler(self)

            return self._value

    def initialize(self):
        self._led1 = MockWiring.MockPin()
        self._rgb = MockWiring.MockPin(value='off')
        self._btn1 = MockWiring.MockPin(0, irq_handler=self.btn1_irq_handler)
        self.cumulative_lightsleep_time_ms = 0
        self.cumulative_deepsleep_time_ms = 0
        self._gps_enable = MockWiring.MockPin()
        self.gps_timer = Timer(duration_ms=self.MOCK_TIME_TO_FIX_MS, event=self.gps_fix_event)


    def btn1_irq_handler(self, pin):
        pin_value = pin.value()
        if pin_value == 1:
            self.trigger_event(self.btn_down_event)
        elif pin_value == 0:
            self.trigger_event(self.btn_up_event)

    @property
    def btn1(self):
        return self._btn1.value()

    @btn1.setter
    def btn1(self, value):
        self._btn1.value(value)

    def lightsleep(self, time_ms):
        self.cumulative_lightsleep_time_ms += time_ms

    def deepsleep(self, time_ms):
        self.cumulative_deepsleep_time_ms += time_ms
        self._wake_reason = 'TIMER'

    def gps_wake(self):
        self._gps_enable.value(1)
        self.gps_fix_event.kwargs = self.MOCK_LOCATION
        self.gps_timer.reset()

    def gps_sleep(self):
        self._gps_enable.value(0)
        self.gps_timer.cancel()

    def gps_update(self):
        self.gps_timer.check()

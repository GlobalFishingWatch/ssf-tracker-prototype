# Wiring for the ESP32-S3 development device
#
# Note that this inherits the app-facing interface from Wiring
# this is so that base class can be used for testing outside the hardware device
# and this implementation can be used inside the device

from wiring import Wiring
from machine import Pin
from machine import UART
from machine import lightsleep
import machine
import micropython
import neopixel
import nmea

micropython.alloc_emergency_exception_buf(100)


# IrqPinEventHandler
# A class for handling hardware interrupts from Pin irg
# triggers a state machine Event object
#
# usage:
#    down_event = my_state_machine.get_event('button_down')
#    up_event = my_state_machine.get_event('button_up')
#    btn = Pin(4, Pin.IN, Pin.PULL_UP)
#    handler = IrqPinEventHandler(pin_rising_event=up_event, pin_falling_event=down_event)
#    btn.irq(handler=handler.handle_irq, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
#
# class IrqPinEventHandler(object):
#     def __init__(self, event=None):
#         self.schedule_fn = self.dispatch
#         self.event = event
#
#     def handle_irq(self, pin):
#         # handle the immediate interrupt
#         # We can't allocate memory or use floating point inside irg handlers, so
#         # don't do any work here - just schedule a callback that will run in the main thread
#         #
#         # NOTE: we store the callback function in __init__ because creating a bound function
#         # allocates memory, so we can't do that here.
#         #
#         # see: https://docs.micropython.org/en/latest/reference/isr_rules.html
#         micropython.schedule(self.schedule_fn, pin.irq().flags())
#
#     def dispatch(self, pin_flags):
#         # trigger the event
#         if pin_flags & Pin.IRQ_RISING:
#             self.event.trigger()
#         elif pin_flags & Pin.IRQ_FALLING:
#             self.event.trigger()


class RGB(object):
    COLORS = {
        'red': (20, 0, 0),
        'green': (0, 20, 0),
        'blue': (0, 0, 20),
        'yellow': (20, 20, 0),
        'white': (20, 20, 20),
        'off': (0, 0, 0)
    }

    def __init__(self, pin):
        self.rgb = neopixel.NeoPixel(Pin(pin), 1)
        self._value = 'off'

    def value(self, x=None):
        if x is None:
            return self._value
        else:
            self.rgb.fill(RGB.COLORS[x])
            self.rgb.write()
            self._value = x
        return None     # explicit return for clarity


class WiringESP32(Wiring):
    def __init__(self, **kwargs):
        self._event_trigger_fn = self.trigger_event  # store a reference to the bound function
        super(WiringESP32, self).__init__(**kwargs)

    def lightsleep(self, time_ms):
        lightsleep(time_ms)

    def initialize(self):
        self._led1 = Pin(self.config.get('LED1_PIN', 5), Pin.OUT)
        self._led1.value(0)

        self._rgb = RGB(self.config.get('RGB_PIN', 48))
        self._rgb.value('off')

        self._btn1 = Pin(self.config.get('BTN1_PIN', 4), Pin.IN)
        self._btn1.irq(handler=self.btn1_irq_handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

        self._gps_enable = Pin(self.config.get('GPS_ENABLE_PIN', 8), Pin.OUT)
        self._gps_enable.value(1)

        self._gps_uart = UART(1, baudrate=9600)     # Pins 9 and 10 on the EPS32 DEV C board

        # Turn on just minimum info (RMC only, basic location):
        self._gps_uart.write(nmea.create_sentence('PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'))
        self._gps_uart.write('\r\n')

        # Set update rate to once a second (1hz) which is what you typically want.
        self._gps_uart.write(nmea.create_sentence('PMTK220,1000'))
        self._gps_uart.write('\r\n')

    def gps_update(self):
        sentence = self._gps_uart.readline()
        if sentence:
            sentence = sentence.decode().strip()
            message = nmea.parse_sentence(sentence)
            if 'error' not in message and message.get('sentence_type') == 'GPRMC':
                if message['fix_quality'] is not None and message['fix_quality'] >= 1:
                    # we have a fix, so store the fix details and trigger event
                    self.gps_fix_event.kwargs = message
                    self.gps_fix_event.schedule()

    def btn1_irq_handler(self, pin):
        # handle the immediate interrupt
        # We can't allocate memory or use floating point inside irg handlers, so
        # don't do any work here - just schedule a callback that will run in the main thread
        #
        # NOTE: we store the callback function in __init__ because creating a bound function
        # allocates memory, so we can't do that here.
        #
        # see: https://docs.micropython.org/en/latest/reference/isr_rules.html

        pin_value = pin.value()
        if pin_value == 1:
            micropython.schedule(self._event_trigger_fn, self.btn_down_event)
        elif pin_value == 0:
            micropython.schedule(self._event_trigger_fn, self.btn_up_event)

    def wake_reason(self):
        # reset_cause = machine.reset_cause()
        wake_reason = machine.wake_reason()

        if wake_reason is machine.PIN_WAKE:
            wake_reason = 'PIN'
        elif wake_reason is machine.TIMER_WAKE:
            wake_reason = 'TIMER'
        else:
            wake_reason = 'RESET'

        return wake_reason

        # if reset_cause is machine.HARD_RESET:
        #     reset_cause = 'HARD_RESET'
        # elif reset_cause is machine.PWRON_RESET:
        #     reset_cause = 'PWRON_RESET'
        # elif reset_cause is machine.WDT_RESET:
        #     reset_cause = 'WDT_RESET'
        # elif reset_cause is machine.DEEPSLEEP_RESET:
        #     reset_cause = 'DEEPSLEEP_RESET'
        # elif reset_cause is machine.SOFT_RESET:
        #     reset_cause = 'SOFT_RESET'

        # wake_reason = machine.wake_reason()
        # if wake_reason is machine.PIN_WAKE:
        #     wake_reason = 'PIN_WAKE'
        # elif wake_reason is machine.EXT0_WAKE:
        #     wake_reason = 'EXT0_WAKE'
        # elif wake_reason is machine.EXT1_WAKE:
        #     wake_reason = 'EXT1_WAKE'
        # elif wake_reason is machine.TIMER_WAKE:
        #     wake_reason = 'TIMER_WAKE'
        # elif wake_reason is machine.TOUCHPAD_WAKE:
        #     wake_reason = 'TOUCHPAD_WAKE'
        # elif wake_reason is machine.ULP_WAKE:
        #     wake_reason = 'ULP_WAKE'

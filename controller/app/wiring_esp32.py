# Wiring for the ESP32-S3 development device
#
# Note that this inherits the app-facing interface from Wiring
# this is so that base class can be used for testing outside the hardware devive
# and this implementation can be used inside the device

from wiring import Wiring
from machine import Pin
from machine import lightsleep
import machine
import micropython

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
class IrqPinEventHandler(object):
    def __init__(self, pin_rising_event=None, pin_falling_event=None):
        self.schedule_fn = self.dispatch
        self.event = event

    def handle_irq(self, pin):
        # handle the immediate interrupt
        # We can't allocate memory or use floating point inside irg handlers, so
        # don't do any work here - just schedule a callback that will run in the main thread
        #
        # NOTE: we store the callback function in __init__ because creating a bound function
        # allocates memory, so we can't do that here.
        #
        # see: https://docs.micropython.org/en/latest/reference/isr_rules.html
        micropython.schedule(self.schedule_fn, pin.irq().flags())

    def dispatch(self, pin_flags):
        # trigger the event
        if pin_flags & Pin.IRQ_RISING:
            self.pin_rising_event.trigger()
        elif pin_flags & Pin.IRQ_FALLING:
            self.pin_falling_event.trigger()




class WiringESP32(Wiring):
    def lightsleep(self, time_ms):
        lightsleep(time_ms)

    def initialize(self):
        self._led1 = Pin(self.config.get('LED1_PIN', 5), Pin.OUT)
        self._led1.value(0)

        self._event_trigger_fn = self.trigger_event  # store a reference to the bound function

        self._btn1 = Pin(self.config.get('BTN1_PIN', 4), Pin.IN, Pin.PULL_UP)
        self._btn1.irq(handler=self.btn1_irq_handler,
                       trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                       wake=machine.SLEEP | machine.DEEPSLEEP)

        # self._btn1_up_irq_handler = IrqEventHandler(event=self.btn_up_event)
        # self._btn1_down_irq_handler = IrqEventHandler(event=self.btn_down_event)
        # self._btn1.irq(handler=self._btn1_up_irq_handler.handle_irq, trigger=Pin.IRQ_RISING)
        # self._btn1.irq(handler=self._btn1_down_irq_handler.handle_irq, trigger=Pin.IRQ_FALLING)


    def btn1_irq_handler(self, pin):
        # handle the immediate interrupt
        # We can't allocate memory or use floating point inside irg handlers, so
        # don't do any work here - just schedule a callback that will run in the main thread
        #
        # NOTE: we store the callback function in __init__ because creating a bound function
        # allocates memory, so we can't do that here.
        #
        # see: https://docs.micropython.org/en/latest/reference/isr_rules.html

        # pin_flags = pin.irq.flags()
        # if pin_flags & Pin.IRQ_RISING:
        #     micropython.schedule(self._event_trigger_fn, self.btn_up_event)
        # elif pin_flags & Pin.IRQ_FALLING:
        #     micropython.schedule(self._event_trigger_fn, self.btn_down_event)

        pin_value = pin.value()
        if pin_value == 1:
            micropython.schedule(self._event_trigger_fn, self.btn_up_event)
        elif pin_value == 0:
            micropython.schedule(self._event_trigger_fn, self.btn_down_event)

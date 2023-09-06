#Setup File
from util import RGB
import machine
import esp32
from machine import deepsleep
from machine import lightsleep
from micropython import schedule

from machine import Pin
from time import sleep

#Define max lines of location log
max_lines = 10

#Create instance of RGB class in util.py
color = RGB()

# Set up sleep and interupts
def wake_msg():
    reset_cause = machine.reset_cause()
    if reset_cause is machine.HARD_RESET:
        reset_cause = 'HARD_RESET'
    elif reset_cause is machine.PWRON_RESET:
        reset_cause = 'PWRON_RESET'
    elif reset_cause is machine.WDT_RESET:
        reset_cause = 'WDT_RESET'
    elif reset_cause is machine.DEEPSLEEP_RESET:
        reset_cause = 'DEEPSLEEP_RESET'
    elif reset_cause is machine.SOFT_RESET:
        reset_cause = 'SOFT_RESET'

    wake_reason = machine.wake_reason()
    if wake_reason is machine.PIN_WAKE:
        wake_reason = 'PIN_WAKE'
    elif wake_reason is machine.EXT0_WAKE:
        wake_reason = 'EXT0_WAKE'
    elif wake_reason is machine.EXT1_WAKE:
        wake_reason = 'EXT1_WAKE'
    elif wake_reason is machine.TIMER_WAKE:
        wake_reason = 'TIMER_WAKE'
    elif wake_reason is machine.TOUCHPAD_WAKE:
        wake_reason = 'TOUCHPAD_WAKE'
    elif wake_reason is machine.ULP_WAKE:
        wake_reason = 'ULP_WAKE'
    return reset_cause,wake_reason


def irq_scheduled(pin):
    print(f'irq {pin.value()}')

def irq_handler(pin):
    schedule(irq_scheduled, pin)


wake1 = Pin(15, mode = Pin.IN)
wake1.irq(handler=irq_handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, wake=machine.DEEPSLEEP)
esp32.wake_on_ext0(pin = wake1, level = esp32.WAKEUP_ALL_LOW)

wake2 = Pin(14, mode = Pin.IN)
wake2.irq(handler=irq_handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, wake=machine.DEEPSLEEP)
esp32.wake_on_ext0(pin = wake2, level = esp32.WAKEUP_ALL_LOW)

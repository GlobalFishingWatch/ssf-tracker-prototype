# main.py
# this is the main app for the microcontroller
# runs after boot.py



from config import load_config
from config import configure_logger
from app import App
from wiring_esp32 import WiringESP32

# LOAD CONFIG
config_filename = './config.json'
app_config = load_config(config_filename)

# SET UP LOGGING
log = configure_logger(app_config)
log.info('Starting App...')

# app = App(WiringESP32, log=log, config=app_config)
# app.initialize()
# app.run()


import machine
import esp32
from machine import deepsleep
from machine import lightsleep
from micropython import schedule

from machine import Pin
from time import sleep


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
    log.info(f'irq {pin.value()}')

def irq_handler(pin):
    schedule(irq_scheduled, pin)


led = Pin (5, Pin.OUT)
wake1 = Pin(4, mode = Pin.IN)
# wake1.irq(handler=irq_handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, wake=machine.SLEEP)
esp32.wake_on_ext0(pin = wake1, level = esp32.WAKEUP_ANY_HIGH)

def run_test_deep_sleep():
    log.info(wake_msg())
    #blink LED
    led.value(1)
    sleep(0.5)
    led.value(0)
    sleep(0.5)

    # wait 5 seconds so that you can catch the ESP awake to establish a serial communication later
    # you should remove this sleep line in your final script
    sleep(2)

    log.info('Going into deep sleep...')
    sleep(1)

    #sleep for 10 seconds (10000 milliseconds)
    deepsleep(10000)


def run_test_light_sleep():
    while True:
        log.info(wake_msg())
        #blink LED
        led.value(1)
        sleep(0.5)
        led.value(0)
        sleep(0.5)

        # wait 2 seconds so that you can catch the ESP awake to establish a serial communication later
        # you should remove this sleep line in your final script
        sleep(2)

        log.info('Going into light sleep...')
        sleep(1)

        #sleep for 10 seconds (10000 milliseconds)
        # irq_state = machine.disable_irq()
        # wake1.irq(handler=None)
        lightsleep(10000)
        # wake1.irq(handler=irq_handler)
        # machine.enable_irq(irq_state)

def run_test_sleep():
    while True:
        log.info(wake_msg())
        #blink LED
        led.value(1)
        sleep(0.5)
        led.value(0)
        sleep(0.5)

        # wait 2 seconds so that you can catch the ESP awake to establish a serial communication later
        # you should remove this sleep line in your final script
        sleep(2)

        log.info('Going into sleep...')

        #sleep for 10 seconds (10000 milliseconds)
        sleep(10)

def blink():
    while True:
        led.value(not led.value())
        sleep(0.5)

# run_test_deep_sleep()
# run_test_light_sleep()
# run_test_sleep()
blink()

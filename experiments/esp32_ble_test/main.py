# BLE Test server in micropython
# Tested on the Arduino Nano ESP32

import sys

sys.path.append("")

from micropython import const
from machine import Pin

import uasyncio as asyncio
import aioble
import bluetooth


led1 = Pin(48, Pin.OUT)

_LED_SERVICE_UUID = bluetooth.UUID('19B10000-E8F2-537E-4F6C-D104768A1214')
_LED_STATE_UUID = bluetooth.UUID('19B10001-E8F2-537E-4F6C-D104768A1214')
TIMEOUT_MS = 5000

_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)
# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000


# Register GATT server.
led_service = aioble.Service(_LED_SERVICE_UUID)
led_characteristic = aioble.Characteristic(
    led_service, _LED_STATE_UUID, read=True, write_no_response=True, capture=True
)
aioble.register_services(led_service)


async def led_state_change():
    led_characteristic.write(b'\x00')
    while True:
        write_connection, value = await led_characteristic.written()
        print(value)
        led1(int.from_bytes(value, 'big'))



# Serially wait for connections. Don't advertise while a central is
# connected.
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="mpy-led",
                services=[_LED_SERVICE_UUID],
                # appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected()
                print("Disconnected")
        except asyncio.CancelledError:
            print("Cancelled")

# Run both tasks.
async def main():
    t1 = asyncio.create_task(led_state_change())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)


asyncio.run(main())


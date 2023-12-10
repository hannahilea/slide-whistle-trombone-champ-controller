# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example acts as a BLE HID keyboard to peer devices.
Attach five buttons with pullup resistors to Feather nRF52840
  each button will send a configurable keycode to mobile device or computer
"""
import time
import board
from digitalio import DigitalInOut, Direction

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

button_1 = DigitalInOut(board.A2) #D11)
button_1.direction = Direction.INPUT

hid = HIDService()

device_info = DeviceInfoService(software_revision=adafruit_ble.__version__,
                                manufacturer="Adafruit Industries")
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
scan_response.complete_name = "CircuitPython HID"

ble = adafruit_ble.BLERadio()
ble.name = "Hannex Feather Trombone Champ"
if not ble.connected:
    print("advertising")
    ble.start_advertising(advertisement, scan_response)
else:
    print("already connected")
    print(ble.connections)

kbd = Keyboard(hid.devices)
kl = KeyboardLayoutUS(kbd)
while True:
    while not ble.connected:
        pass
    print("Start typing:")

    b_value = False
    while ble.connected:
        # check/update button state
        new_value = button_1.value
        if b_value != new_value:
            b_value = new_value
            print("Value changed!") # debug
            if b_value:
#               print("button pressed")  # for debug in REPL
                kbd.press(Keycode.E)
            else:
                kbd.release(Keycode.E)

    ble.start_advertising(advertisement)

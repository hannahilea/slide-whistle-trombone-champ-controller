#!/usr/bin/env python3
"""
Controller for Trombone Champ by acting as a BLE HID keyboard to peer devices.
  Attach one button with a pullup resistor and one potentiometer to Feather nRF52840
  The button will send a configurable keycode to mobile device or computer;
  the slider will send a mouse movement in the y-axis direction to mobile device or computer.
"""
import board
import math
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# Global constants
MAX_SLIDER_Y_VALUE = 900 # roughly corresponds to pixel height of screen
CHANGE_TOLERANCE = 12    # "pixel" change threshold; above this tolerance triggers mouse movement
NUM_SMOOTHED_VALUES = 60 # Buffer for running average of slider values

# Initialize the onboard controls
button_1 = DigitalInOut(board.A2)
button_1.direction = Direction.INPUT
pot_in = AnalogIn(board.A1)

# Set up bluetooth connection
hid = HIDService()
device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries"
)
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
scan_response.complete_name = "CircuitPython HID"

ble = adafruit_ble.BLERadio()
ble.name = "Hannex Trombone Champ"
if not ble.connected:
    print("advertising")
    ble.start_advertising(advertisement, scan_response)
else:
    print("already connected")
    print(ble.connections)

# Set up keyboard
kbd = Keyboard(hid.devices)
kl = KeyboardLayoutUS(kbd)
mouse = Mouse(hid.devices)

# Helper functions for slider mapping
def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def map_pot_percent(voltage, v_min, v_max):
    f = (voltage - v_min) / (v_max - v_min)
    return math.trunc(f * 100)

def main_event_loop():
    while True:
        while not ble.connected:
            pass
        print("Bluetooth connected!")

        button_state = False
        slider_buffer = [0 for _ in range(NUM_SMOOTHED_VALUES)]
        slider_previous = 0.0
        x = get_voltage(pot_in)
        while ble.connected:
            # Get slider values
            voltage = get_voltage(pot_in)
            slider_current = MAX_SLIDER_Y_VALUE * map_pot_percent(voltage, 1.62, 2.13) / 100
            slider_buffer.append(slider_current)
            slider_buffer.pop(0)

            slider_current = sum(slider_buffer) / NUM_SMOOTHED_VALUES
            diff = math.trunc(slider_previous - slider_current)

            # check/update button state
            new_value = button_1.value
            if button_state != new_value:
                button_state = new_value
                print("Value changed!")  # debug
                if button_state:
                    kbd.press(Keycode.SPACE)
                    print(x, voltage, x - voltage)
                    pass
                else:
                    kbd.release(Keycode.SPACE)
                    pass

            # Use slider voltage to update mouse position
            elif abs(diff) >= CHANGE_TOLERANCE:
                #print(slider_current, voltage, diff)
                mouse.move(y=diff)
                print("UPDATING: ", slider_previous, slider_current, diff)
                slider_previous = slider_current

        ble.start_advertising(advertisement)


if __name__ == "__main__":
    main_event_loop()

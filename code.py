"""
This example acts as a BLE HID keyboard to peer devices.
Attach one button with a pullup resistor and one potentiometer to Feather nRF52840
  the button will send a configurable keycode to mobile device or computer
  the slider will send a mouse movement in the y-axis direction to mobile device or computer
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

button_1 = DigitalInOut(board.A2)  # D11)
button_1.direction = Direction.INPUT
pot_in = AnalogIn(board.A1)

hid = HIDService()

device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries"
)
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
mouse = Mouse(hid.devices)


def get_voltage(pin):
    return (pin.value * 3.3) / 65536


def map_pot_percent(voltage, v_min, v_max):
    f = (voltage - v_min) / (v_max - v_min)
    return math.trunc(f * 100)


MAX_SLIDER_Y_VALUE = 700
CHANGE_TOLERANCE = 10
NUM_SMOOTHED_VALUES = 60

while True:
    while not ble.connected:
        pass
    print("Start typing:")

    button_state = False
    slider_value = 0.0
    slider_values = [0 for _ in range(NUM_SMOOTHED_VALUES)]
    while ble.connected:
        # check/update button state
        new_value = button_1.value
        if button_state != new_value:
            button_state = new_value
            print("Value changed!")  # debug
            if button_state:
                print("Down")
                # kbd.press(Keycode.E) # TODO-future: use different key value for click?
            else:
                # kbd.release(Keycode.E)
                mouse.move(y=100)

        # check/update mouse state
        voltage = get_voltage(pot_in)
        slider_current = MAX_SLIDER_Y_VALUE * map_pot_percent(voltage, 1.62, 2.13) / 100
        slider_values.append(slider_current)
        slider_values.pop(0)

        slider_current = sum(slider_values)/NUM_SMOOTHED_VALUES
        diff = math.trunc(slider_value - slider_current)

        # print('y:{0}, V:{1}; raw:{2}'.format(slider_current, voltage, pot_in.value))
        if abs(diff) >= CHANGE_TOLERANCE:
            print(slider_current, voltage, diff)
            mouse.move(y=diff)
            slider_value = slider_current

    ble.start_advertising(advertisement)

# Trombone Champ Controller 
Nifty name TBD. 

## Dev log
### Punch list:
Project:
- [ ] Try out breadboard with game
- [ ] Additional button/switch for on-off  (e.g. whether or not to send mouse commands...)
- [ ] Move electronics to devboard + slide whistle 
- [ ] Clean up documentation
- [ ] Stretch: print pcb?

Meta: 
- [ ] Shift over to VSCode instead of Mu Editor, document workflow
- [ ] Better-structure project code (separate files, main entrypoint, etc)

### 29 Oct 2024
- AF poked at circuitry, simplified some items
- We drew up schematic in [TinkerCAD](https://www.tinkercad.com/things/6Mko6kfHVgg-trombonechamp-1)
    - see downloaded image! also schematic
- Other component data sheet info:
    - yellow switch (adafruit): https://cdn-shop.adafruit.com/product-files/5516/5516_switch.png
    - slide potentiometer: https://www.adafruit.com/product/4219 and https://cdn-shop.adafruit.com/product-files/4219/4219_C11375.pdf


### 18 Oct 2024
- Set up mouse input mapping, etc
- Resources for future:
    - https://docs.circuitpython.org/en/latest/shared-bindings/index.html
    - https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-serial-monitor 
    -  https://docs.circuitpython.org/en/latest/docs/library/index.html
    - https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse 

### Initial development
- Starting with https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather 

1. Plugged in battery — lights on/!
2. Plugged in USB cable btween board and macbook air
3. Followed steps to update bootloader:
    1. Ran `pip3 install --user adafruit-nrfutil`
    2. Due to https://stackoverflow.com/questions/35898734/pip-installs-packages-successfully-but-executables-not-found-from-command-line, ran ```echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc```
    1. Downloaded `feather_nrf52840_express_bootloader-0.8.0_s140_6.1.1.zip` from  https://github.com/adafruit/Adafruit_nRF52_Bootloader/releases/tag/0.8.0 and moved to working directory
    2. Ran ```adafruit-nrfutil --verbose dfu serial --package feather_nrf52840_express_bootloader-0.8.0_s140_6.1.1.zip -p /dev/cu.usbmodem1101 -b 115200 --singlebank --touch 1200``` 
        1. Can tab-complete /dev/cu.usbmodem to get value there OR do `ls /dev/cu.*` to find it (as in instructions)
    3. Clicked “reset” button ON THE BOARD (it is tiny!)
        1. …now board will show up in Finder!
        2. 

4. Install CircuitPython! Followed https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/circuitpython, i.e., download file and drag onto plugged in board as visible in Finder. then it Just Works™ 
    1. NOTE: ignored all of the arduino setup stuff in the original doc! Skipped to https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/circuitpython 
5. Install Mu Editor (necessary? don’t know enough to know…) following https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor 
    1. - did the demo to prove to ourselves it worked! hello world

——
Next: made an *external* LED blink (connected to A3)
```
import board
import digitalio
import time

led = digitalio.DigitalInOut(board.A3)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
```
——
Next: read in from A3 (as digital) 
```
import board
import digitalio
import time

input = digitalio.DigitalInOut(board.A3)
input.direction = digitalio.Direction.INPUT

while True:
    print(input.value)
    time.sleep(0.1)
```
—

Next: light external light on button push (well, first on “change of wire in breadboard”, then button)
from button
https://www.adafruit.com/product/5516 
datasheet: https://cdn-shop.adafruit.com/product-files/5516/5516_switch.png 
```
import board
import digitalio

input = digitalio.DigitalInOut(board.A3)
input.direction = digitalio.Direction.INPUT

led = digitalio.DigitalInOut(board.A5)
led.direction = digitalio.Direction.OUTPUT

bValue = input.value
while True:
    bNew = input.value
    led.value = bNew
    if bNew != bValue:
        print("Changed value!", bValue)
        bValue = bNew
```
—
Next: read analog in from current button 
```
import board
import analogio

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

analog_in = analogio.AnalogIn(board.A3)
while True:
    print('Voltage: ' + (get_voltage(analog_in),) + '; Value: ' + analog_in)
    time.sleep(0.1)
```

—
Next: add potentiometer! 
https://www.adafruit.com/product/4219
datasheet: https://cdn-shop.adafruit.com/product-files/4219/4219_C11375.pdf 
```
import board
import digitalio
import analogio
import time
import math

def get_voltage(pin):
    return (pin.value * 3.3) / 65536
    
def map_pot(voltage, v_min, v_max):
    f =(voltage - v_min) / (v_max - v_min)
    return math.trunc(f * 100)
    
button_in = digitalio.DigitalInOut(board.A2)
button_in.direction = digitalio.Direction.INPUT

pot_in = analogio.AnalogIn(board.A1)
while True:
    voltage = get_voltage(pot_in)
    slide_value = map_pot(voltage, 1.7, 2.18)
    print('Pot value: {0}%, Voltage: {1}; raw input: {2}; button value {3}'.format(slide_value, voltage, pot_in.value, button_in.value))
    time.sleep(0.1)

```
——
Now…….bluetooth keyboard interaction!!
Following: https://learn.adafruit.com/ble-hid-keyboard-buttons-with-circuitpython/ble-keyboard-buttons 

1. downloaded project bundle (libs) from https://learn.adafruit.com/ble-hid-keyboard-buttons-with-circuitpython/ble-keyboard-buttons-libraries-and-code 
2. Running CircuitPyton 8.2.8, so copied in lib/ file from downloaded zip to CIRCUITPY/lib/ folder

———
Other:
- Components: 



Keyboard and mouse tutorial: https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse 
- [ ] 

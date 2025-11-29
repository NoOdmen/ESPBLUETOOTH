# Blinking LED with Micropython and ESP32

This proyect makes a simple and a RGB LED blink or fade using Micropython on a ESP32.

This project uses the `esptool` and `rshell` Python libraries to flash Micropython and interact with the ESP32.

`esptool` is used to install the Micropython firmware on to the ESP32. More information at [https://github.com/espressif/esptool](https://github.com/espressif/esptool).

`rshell` is used to interact with the ESP32, write some code directly on it and see its output. More information at [https://github.com/dhylands/rshell](https://github.com/dhylands/rshell).

## Setup

### Install

If you don't have Python 3 installed, download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).

Setup and activate a virtual environment.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the libraries listed inside the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

Verify that the installed libraries work correctly.

```bash
esptool.py --help
rshell --help
```

### Flash

To be able to use Micropython on the ESP32, the Micropython firmware needs to be flashed on to it. This only needs to be done once and should be reversible by uploading a project from the Arduino IDE.

Download the Micropython firmware from [http://micropython.org/download/esp32/](http://micropython.org/download/esp32/) and place it inside the same folder from where you want to execute the commands.

The current stable version is `esp32-idf3-20191220-v1.12.bin` (or a newer version if available).

In order to use each library you need to tell it which device it should work with by specifying the port. For that you need to find out which COM port corresponds to the connected ESP32.

**Windows:**
- Open Device Manager and look under "Ports (COM & LPT)" for your ESP32 device
- Usually it should be `COM3`, `COM4`, etc. on Windows

**Linux:**
- Use `ls /dev/tty*` to find the device. Usually it should be `/dev/ttyUSB0`

**Mac:**
- Usually it should be `/dev/tty.SLAB_USBtoUART` or `/dev/tty.usbserial-*`

Use the port in the port part of the next command. Replace `COM3` with your actual port.

**Windows:**
```bash
esptool.py --chip esp32 --port COM3 erase_flash
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 ESP32_GENERIC-20250911-v1.26.1.bin
```

**Linux/Mac:**
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ESP32_GENERIC-20250911-v1.26.1.bin
```

> **Note:** Replace `ESP32_GENERIC-20250911-v1.26.1.bin` with the actual firmware file name you downloaded.

### Troubleshoot

**Windows:**
If you get a permission error or the port is not found, make sure:
- The ESP32 is properly connected via USB
- You have the correct COM port (check Device Manager)
- No other program is using the serial port

**Linux:**
If an exception saying `[Errno 13] Permission denied: '/dev/ttyUSB0'` appears while executing the previous commands, add your current user to the dialout group.

```bash
sudo usermod -a -G dialout ${USER}
```

Logout and login to apply this change.

### Try out

Access the interactive console.

**Windows:**
```bash
rshell --port COM3 repl
```

**Linux/Mac:**
```bash
rshell --port /dev/ttyUSB0 repl
```

Read a value from the temperature and magnetic field (hall effect) sensor.

```python
import esp32

esp32.raw_temperature()
esp32.hall_sensor()
```

Press <kbd>CTRL</kbd> + <kbd>X</kbd> to exit.

## Pinout

The pinout of my ESP32 looks like this.

![ESP32 Pinout](images/ESP32_pinout.jpg)

> Image from [http://forum.fritzing.org/t/esp32s-hiletgo-dev-boad-with-pinout-template/5357](http://forum.fritzing.org/t/esp32s-hiletgo-dev-boad-with-pinout-template/5357)

You can find the pinout for other ESP32's by searching for **pinout**
on [http://esp32.net/](http://esp32.net/) and follow those links.

## Single LED

### Setup circuit

![Single LED](images/LED_circuit.jpg)

Connect the ground pin to the shorter leg.
Connect pin 23 to the other leg, with a 470Ω resistor in between
to prevent de LED from burning out. If you don't have a resistor with that exact value, just use something close enough.

Since I didn't have 470Ω resistors, I used two 1kΩ resistors in parallel,
to get 500Ω. The formula for that is `1/Rt = 1/R1 + 1/R2 + ...`.
In this case `1/Rt = 1/1000 + 1/1000` --> `1/Rt = 2/1000` -->
`Rt = 1000/2` --> `Rt = 500`.

You could also use two 220Ω resistors in series/sequentially to add up to 440Ω.

### Connect to interactive shell

**Windows:**
```bash
rshell --port COM3 repl
```

**Linux/Mac:**
```bash
rshell --port /dev/ttyUSB0 repl
```

> **Note:** Replace `COM3` with your actual COM port on Windows.

You can exit the shell by pressing <kbd>CTRL</kbd> + <kbd>X</kbd>.

If you can't reconnect afterwards, you might need to restart your ESP32
by pressing the `EN` button.

### Try manually

Once you are connected to the interactive shell,
try these commands to turn the LED on and off.

```python
import machine

led = machine.Pin(23, machine.Pin.OUT)

led.value(1)
led.value(0)
```

If the LED doesn't turn on, it might just be connected the wrong way around.
Connect the ground pin to the longer leg and pin 23 to the other leg
and try again.

### Try examples

After verifying that the circuit works correctly,
upload the examples and execute them after a restart.
The uploaded file has to be called `main.py`
and gets executed when the ESP32 starts up.

[blink.py](blink.py) blinks the LED once long and twice short.

**Windows:**
```bash
copy blink.py main.py
ampy --port COM3 put main.py
# Restart the ESP32 to execute it by pressing the EN button
```

**Linux/Mac:**
```bash
cp blink.py main.py
ampy --port /dev/ttyUSB0 put main.py
# Restart the ESP32 to execute it by pressing the EN button
```

[fade.py](fade.py) fades the LED on and off
according to a sine wave using pulse width modulation (PWM).

**Windows:**
```bash
copy fade.py main.py
ampy --port COM3 put main.py
```

**Linux/Mac:**
```bash
cp fade.py main.py
ampy --port /dev/ttyUSB0 put main.py
```

## RGB LED

### Setup circuit

![RGB LED](images/RGB_circuit.jpg)

Connect the ground pin to the longer leg.
Connect pin 23, 22, and 21 with the other legs,
with a 470Ω resistors between each pin and the LED.

[fade-rgb.py](fade-rgb.py) fades the RGB LED using three sine waves,
with the start of each sine wave shifted from the others
to make the three color light up at different times.

**Windows:**
```bash
copy fade-rgb.py main.py
ampy --port COM3 put main.py
```

**Linux/Mac:**
```bash
cp fade-rgb.py main.py
ampy --port /dev/ttyUSB0 put main.py
```

[fade-hsv.py](fade-hsv.py) fade the RGB LED by converting
from the HSV (Hue, Saturation, Value) color space to RGB
to have three times in a cycle where only one color is lit up.

**Windows:**
```bash
copy fade-hsv.py main.py
ampy --port COM3 put main.py
```

**Linux/Mac:**
```bash
cp fade-hsv.py main.py
ampy --port /dev/ttyUSB0 put main.py
```

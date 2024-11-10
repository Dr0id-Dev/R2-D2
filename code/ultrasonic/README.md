# Raspberry Pi Zero 2 W - ST7789 Display Hello World

This sub-project demonstrates how to use an Adafruit ST7789 LCD display with a Raspberry Pi Zero 2 W to show a simple "Hello World" message with some test patterns. The program initialises the display, draws some coloured rectangles for testing, and displays centred text.

## Hardware 

- Raspberry Pi Zero 2 W
- Adafruit ST7789 Display (240x280 resolution)
- Jumper wires
- Breadboard 

## Pin Connections

The ST7789 display is connected to the Raspberry Pi Zero 2 W using the following pin mapping:

| ST7789 Pin | Raspberry Pi Pin | Pin Number/Name |
|------------|------------------|-----------------|
| VCC        | 3.3V            | Pin 1           |
| GND        | Ground          | Pin 6           |
| SCL        | SPI0 SCLK       | GPIO 11        |
| SDA        | SPI0 MOSI       | GPIO 10        |
| RES        | Reset           | GPIO 24        |
| DC         | Data/Command     | GPIO 25        |
| CS         | Chip Select     | GPIO 8 (CE0)   |
| BL         | 3.3V            | Pin 1           |

## Software Prerequisites

1. Enable SPI interface:
```bash
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable
```

2. Install required packages:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip
sudo pip3 install adafruit-circuitpython-rgb-display
sudo pip3 install Pillow
```

## Installation

1. Clone or download this project to your Raspberry Pi.

2. Make sure the script is executable:
```bash
chmod +x hello_world.py
```

3. Run the script:
```bash
sudo python3 hello_world.py
```

## Expected Output

When running correctly, you should see:
1. A red rectangle in the top-left corner
2. A green rectangle in the top-right corner
3. A blue rectangle in the bottom-right corner
4. "Hello, World!" text centred on the display in white

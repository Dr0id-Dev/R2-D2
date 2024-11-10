#!/usr/bin/python3
import board
import digitalio
import adafruit_rgb_display.st7789 as st7789
from PIL import Image, ImageDraw, ImageFont
import subprocess

# Configuration for CS and DC pins:
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D17)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=280,
    height=240,
    x_offset=0,
    y_offset=80,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width   # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)

# Draw a black filled box as the background
draw.rectangle((0, 0, width, height), outline=0, fill=0)
disp.rotation = 90

# Load a TTF font.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# Draw the text
text = "Hello, World!"
font_width, font_height = font.getsize(text)
# Calculate text position to center it
x = (width - font_width) // 2
y = (height - font_height) // 2

# Draw the text
draw.text(
    (x, y),
    text,
    font=font,
    fill=(255, 255, 255)
)

# Display image.
disp.image(image)

import numpy as np
import pandas as pd
import spidev
import RPi.GPIO as GPIO
import time
import pathlib
import yaml
import gpiozero

# Read from config.yaml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# SpiDev init
spi = spidev.SpiDev()

# (bus,device) used to connect to SPI device
# 0,0 is placeholder
spi.open(0,0)

# 32 MHz MAX
max_speed_hz = 4800
# Sets Pin Numbering Declaration (Uses board numbering scheme)

GPIO.setmode(GPIO.BOARD)

# Read from sensors
# GPIO 9 (G) & 10 for pressure

# GPIO 20 (G) & 21 for thermo
for x in config['hardware']['sections']:
    spidev.bits_per_word()

# Create .csv file




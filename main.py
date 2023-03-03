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
GPIO.setup()
# GPIO 11 -> Pin 23 for clock
GPIO.setup(23, GPIO.OUT)

# GPIO 9 -> Pin 21 for pressure sensor

GPIO.setup(21, GPIO.IN)

# GPIO 19, 20, 21 -> Pin 35, 38, 40 thermocouple
GPIO.setup(35, GPIO.IN)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

# GPIO 23, 24, 25 -> 16, 18, 22 Multiplexer to send out signal 
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

# GPIO 18, 8 -> 12(OUT), 24(IN) 8 for pressure sensor 
# multiplexer 18 for thermocouple multiplexer
GPIO.setup(12, GPIO.OUT)
GPIO.setup(24, GPIO.IN)


time.sleep(60)
# Read from sensors
for x in config['hardware']['sections']:
    spidev.bits_per_word()

# Create .csv file

import numpy as np
import pandas as pd
import spidev
import RPi.GPIO as GPIO
import time
import pathlib
import yaml
import gpiozero

pressureSensorValue = 0
thermoSensorValue = 0

# Read from config.yaml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# SpiDev init
spi = spidev.SpiDev()

# (bus,device) used to connect to SPI device
# bus is 0, cs 1
spi.open(0,1)

# 32 MHz MAX
max_speed_hz = 4800

# Sets Pin Numbering Declaration (Uses board numbering scheme)
GPIO.setmode(GPIO.BOARD)

# GPIO 11 -> Pin 23 for clock
GPIO.setup(23, GPIO.OUT)

# GPIO 9 -> Pin 21 for pressure sensor
GPIO.setup(21, GPIO.IN)
GPIO.setup(24, GPIO.IN)

# GPIO 19, 20, 21 -> Pin 35, 38, 40 thermocouple
GPIO.setup(35, GPIO.IN) # MiPo
GPIO.setup(38, GPIO.OUT) # MoPi
GPIO.setup(40, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

# GPIO 23, 24, 25 -> 16, 18, 22 Multiplexer to send out signal 
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

# Pressure Sensor Reading
# 23, 24, 25 send out signal to multiplexer in select mode
# Clock value to 1
GPIO.output(23, 1)

GPIO.output(16, 0)
GPIO.output(18, 0)
GPIO.output(22, 0)

# reading 8 bits (1 byte) from pressure sensor
presureSensorValue = spi.readbytes(1)
# binary to decimal 150 psi = 1 megapascal 
# in binary, a percentage of the max value, which is 150 psi


# Thermocouple Sensor 
# Multiplexer to read from thermocouple
GPIO.output(26, 0)

GPIO.output(35, 1)

thermoSensorValue = spi.readbytes(1)
# binary value of temp in degrees

time.sleep(config['software']['poll_rate'])
# Read from sensors
for x in config['hardware']['sections']:
    spidev.bits_per_word()

# Create .csv file

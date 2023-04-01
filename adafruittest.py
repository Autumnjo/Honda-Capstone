import numpy as np
import os
import pandas as pd
#import spidev
#import RPi.GPIO as GPIO
import time
import pathlib
import yaml
import pyudev
import board
import digitalio
import adafruit_max31856 as thermoamp
import busio

from enum import Enum

# Function Definitions

spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

cs = digitalio.DigitalInOut(board.D18)
cs.direction = digitalio.Direction.OUTPUT

thermocouple = thermoamp.MAX31856(spi,cs,thermocouple_type=thermoamp.ThermocoupleType.J)

while True:
    print(thermocouple.temperature)
    time.sleep(2)
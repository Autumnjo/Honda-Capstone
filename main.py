import numpy as np
import pandas as pd
import spidev
import RPi.GPIO as GPIO
import time
import pathlib
import yaml

# Read from config.yaml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# SpiDev init
spi = spidev.SpiDev()
# bus,device used to connect to SPI device
spi.open(bus,device)

# 32 MHz MAX
max_speed_hz = 4800

# Read from sensors
for x in config['hardware']['sections']:
    spidev.bits_per_word()

# Create .csv file




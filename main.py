import numpy as np
import pandas as pd
import spidev
import RPi.GPIO as GPIO
import time
import pathlib
import yaml
import pyudev

##### config.yaml file #####
# Read from config.yaml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

##### USB reading #####
# Context object via pyudev for USB reading
context = pyudev.Context()

# Monitor object for monitoring USB device
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

# Begin USB monitoring
monitor.start()

##### Initialize board/pins #####
# SpiDev init
spi = spidev.SpiDev()

# (bus,device) used to connect to SPI device
# bus is 0, cs 1
spi.open(0,1)

# 32 Mhz MAX
spi.max_speed_hz = 250000 # set speed to 250 Khz

# Sets Pin Numbering Declaration (Uses BCM numbering scheme)
GPIO.setmode(GPIO.BCM)

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

# Thermocouple Sensor 
# Multiplexer to read from thermocouple
GPIO.output(26, 0)
GPIO.output(35, 1)

##### Read data #####
pressurePin = 21
thermoPin = 35
data = []
usb_present = False

try:
    while True:     # endless loop, press ctrl+c to exit
        # Read from sensors
        device = monitor.poll()
        if device:
            if device.action == 'add':
                usb_present = True
                while(usb_present):
                    # reading 8 bits (1 byte) from pressure sensor
                    pressureRead = spi.xfer2([0x80 | pressurePin, 0x00])
                    pressure = ((pressureRead[0] & 0x07) << 8) | pressureRead[1]

                    # binary to decimal 150 psi = 1 megapascal 
                    # in binary, a percentage of the max value, which is 150 psi
                    thermoRead = spi.xfer2([0x80 | thermoPin, 0x00])
                    thermo = ((thermoRead[0] & 0x07) << 8) | thermoRead[1]

                    # to .csv
                    data.append(pressure, thermo)
                    df = pd.DataFrame(data, columns=['Pressure_Data', 'Thermo_Data'])
                    df.to_csv('data.csv', index=False)

                    # sleep for poll rate time
                    time.sleep(config['software']['poll_rate'])
                    usb_present = False
            elif device.action == 'remove' and usb_present:
                usb_present = False
finally:
    spi.close()     # close port before exit

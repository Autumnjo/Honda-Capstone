import numpy as np
import os
import pandas as pd
import spidev
import RPi.GPIO as GPIO
import time
import pathlib
import yaml
import pyudev

from enum import Enum

# Function Definitions

class Pin(Enum):
    A0 = 23
    A1 = 24
    A2 = 25
    A3 = 26

def thermosetup(spi_therm):
    reg_0 = [0x00, 0x80] # register code - 0x00, config code - 0b10000000
    reg_1 = [0x01, 0x22] # register code - 0x01, config code - 0b00100010
    
    spi_therm.writebytes(reg_0)
    spi_therm.writebytes(reg_1)

    return

def pressureconversion(raw):
    raw = (raw[0] * 16 * 16)+ raw[1]
    if raw == 0:
        return 0
    
    max_hex = 0x3FFF
    return 2 * (100 * float(raw)/float(max_hex))

def thermoconstruct(raw):
    intpart = (raw[0] << 4) + (raw[1] >> 4) & 15   
#    fracpart = (((raw[1] << 4) & 240) + (raw[2] >> 4) & 30)
#    fracpart = (float)(fracpart)/(float)(2^7)
#    full = (float)(intpart) + (float)(fracpart)
    return intpart

def findUSBs():
    return os.listdir("/media/autumnjo")


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
# SpiDev Init
spi_air = spidev.SpiDev()
spi_therm = spidev.SpiDev()

# (bus,device) used to connect to SPI device
# thermocouple bus is (1, 0)
# airflow bus is (0, 0)
spi_air.open(0,0)
spi_therm.open(1,0)

# 32 Mhz MAX
spi_air.max_speed_hz = 250000 # set speed to 250 Khz
spi_therm.max_speed_hz = 250000 

# Sets Pin Numbering Declaration (Uses BCM numbering scheme)
GPIO.setmode(GPIO.BCM)

# GPIO 23, 24, 25, 26 -> A0, A1, A2, A3 Multiplexer to send out signal 
GPIO.setup(Pin['A0'].value, GPIO.OUT)
GPIO.setup(Pin['A1'].value, GPIO.OUT)
GPIO.setup(Pin['A2'].value, GPIO.OUT)
GPIO.setup(Pin['A3'].value, GPIO.OUT)

# Pressure Sensor Reading
# 23, 24, 25 send out signal to multiplexer in select mode

GPIO.output(Pin['A0'].value, 0)
GPIO.output(Pin['A1'].value, 0)
GPIO.output(Pin['A2'].value, 0)

# Thermocouple Sensor 
# Multiplexer to read from thermocouple
GPIO.output(Pin['A3'].value, 0)

##### Read data #####
data = []
usb_present = False



try:
    while True:     # endless loop, press ctrl+c to exit
        # Read from sensors
        # device = monitor.poll()
        
        usbs = findUSBs()
        print(usbs)
        if len(usbs) > 0:
#            if device.action == 'add':
                usb_present = True
                setup = False
                while(usb_present):
                    if(setup == False):
                        thermosetup(spi_therm)
                        setup = True

                    # reading 2 bytes from pressure sensor
                    pressureRead = spi_air.readbytes(2)
                    pressure = pressureconversion(pressureRead)

                    # binary to decimal 150 psi = 1 megapascal 
                    # in binary, a percentage of the max value, which is 150 psi
                    

                    thermoRead = spi_therm.xfer([0x0E, 0x0D, 0x0C]) # Address of each thermoregister
                    print(thermoRead)
                    thermo = thermoconstruct(thermoRead)
                    #print(thermo) # hhhhhh

                    # to .csv
#                    data.append(pressure, thermo)
#                    df = pd.DataFrame(data, columns=['Pressure_Data', 'Thermo_Data'])
#                    df.to_csv('data.csv', index=False)

                    # sleep for poll rate time
#                    time.sleep(config['software']['poll_rate'])
#                    usb_present = False
#           elif device.action == 'remove' and usb_present:
                # usb_present = False
finally:
    spi_air.close()     # close port before exit
    spi_therm.close()


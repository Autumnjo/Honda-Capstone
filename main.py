import numpy as np
import os
import pandas as pd
import spidev
import RPi.GPIO as GPIO
import time
import pathlib
import yaml
import pyudev
import board
import digitalio
import adafruit_max31856 as thermoamp
from adafruit_bus_device.spi_device import SPIDevice
import busio

from enum import Enum

# Function Definitions

_MAX_PRESSURE_VAL = 0x3FFF 
_P_MAX = 2 # 2 inH2O
_P_MIN = -2
def convert_pressure(raw):
    # Pressure is on a range from 0 to 100% of -2inH2O to 2inH2O
    pressure = raw[0] << 8 | raw[1] # shifts the MSB left 8 and adds the LSB portion
    pressure_percent = 100 * float(pressure)/float(_MAX_PRESSURE_VAL)
    # Apply transfer function
    # Output (%) = 80%/(Pmax - Pmin) * (Pressure_Applied - Pmin) + 10%
    # Rearrange: (Output - 10%)/(Pressure_Applied - Pmin) = 80%/(Pmax - Pmin)
    # Reciprocal: (Pressure_Applied - Pmin)/(Output - 10%) = (Pmax-Pmin)/80%
    # Pressure_Applied = (Pmax - Pmin)(Output - 10%)/80% + Pmin


    return (_P_MAX - _P_MIN) * (pressure_percent - 10)/80 + _P_MIN


_MEDIA_DIRECTORY = "/media/autumnjo"
def findUSBs():
    return os.listdir(_MEDIA_DIRECTORY)

def getUSBDriveDir():
    drives = findUSBs()
    if(len(drives) > 0):
        return _MEDIA_DIRECTORY + "/" + drives[0] # Returns the first USB drive it finds.


##### config.yaml file #####
# Read from config.yaml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Set number of sensors to read
sensors_connected = config['hardware']['sections']

##### USB reading #####
# Context object via pyudev for USB reading
context = pyudev.Context()

# Monitor object for monitoring USB device
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

# Begin USB monitoring
monitor.start()

##### Initialize board/pins #####

spi_temp = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
spi_air = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)


# PINS

class Pins(Enum):
    A0 = digitalio.DigitalInOut(board.D5)
    A1 = digitalio.DigitalInOut(board.D6)
    A2 = digitalio.DigitalInOut(board.D26)
    A3 = digitalio.DigitalInOut(board.D25)
    E_not = digitalio.DigitalInOut(board.D16) # Initializing these to zero enables the decoders
    G_not = digitalio.DigitalInOut(board.D13) # Initializing these to zero enables the decoders

for pin in Pins:
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = 0


temp = thermoamp.MAX31856(spi_temp, Pins.E_not, thermocouple_type=thermoamp.ThermocoupleType.J) # Can utilize this directly for temp readings
airflow = SPIDevice(spi_air, Pins.G_not) # A bit more complicated. We'll see how it pans out.

def decodeAndSetPins(address): # Python performs comparison in integers much faster than binary.
    if(1 & address): # '0001' & <...1> from address
        Pins.A0.value = 1
    else:
        Pins.A0.value = 0

    if(2 & address): # '0010' major check
        Pins.A1.value = 1
    else:
        Pins.A1.value = 0
    
    if(4 & address): 
        Pins.A2.value = 1
    else:
        Pins.A2.value = 0

    if(8 & address): 
        Pins.A3.value = 1
    else:
        Pins.A3.value = 0

    return


##### Read data #####
data = []
usb_present = False
airflow_bytes = bytearray(2) # 2 bytes for the airflow reading. 

_DEFAULT_POLL_RATE = .1 # Can assign from CSV


while True:     # endless loop, press ctrl+c to exit
    # Read from sensors
    # device = monitor.poll()
        
    usbs = findUSBs()
    if len(usbs) > 0:
#         if device.action == 'add':
            usb_present = True
            while(len(findUSBs > 0)):
                for i in range(sensors_connected):
                    decodeAndSetPins(i)
                    temperature = temp.temperature
                    pressure = 0
                    with airflow as spi:
                        if(spi.try_lock()): 
                            spi.readinto(airflow_bytes)
                            pressure = convert_pressure(airflow_bytes)
                            spi.unlock()

                    # to .csv
                    data.append((pressure, temperature, i))
                    df = pd.DataFrame(data, columns=['Pressure_Data', 'Thermo_Data', 'Sensor Number'])
                    df.to_csv('data.csv', index=False)

                    # sleep for poll rate time
                    time.sleep(config['software']['poll_rate'])
                    
#finally:
#    spi_air.close() 
#    spi_therm.close()


#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

import time
from pythonosc import osc_message_builder
from pythonosc import udp_client
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)

time.sleep(2)

def dist_to_pitch(d):
    low = 0.002
    high = 0.005
    too_high = 0.007
    if d > too_high:
        return None
    if d < low:
        d = low
    elif d > high:
        d = high
    pitch_coefficient = (d - low) / (high - low)
    low_pitch = 60
    high_pitch = 72
    pitch = high_pitch - (high_pitch - low_pitch) * pitch_coefficient
    return round(pitch)

old_chs = [0, 0, 0, 0]
samples = 0
# st = time.time()
while True:
    # time.sleep(0.01)
    chs = []
    for i in range(1):
        chs.append(readadc(i, SPICLK, SPIMOSI, SPIMISO, SPICS))
    # print("sps:", samples / (time.time() - st))
    # print(chs)
    if chs[0] > 30 and old_chs[0] > 30:
        print("boom")
        sender.send_message('/a', 50)
    old_chs = chs
    samples += 1

    # sender.send_message('/a', pitch)





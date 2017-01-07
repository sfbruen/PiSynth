#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 17:41:03 2016

@author: thomasbruen
"""

import spidev
from time import sleep
import csv
#import RPi.GPIO as GPIO

DEBUG = False
spi_max_speed = int(4* 1000000) # 20 MHz
bpw = int(8)
V_Ref = 5000 # 5V in mV
Resolution = 2**12 # 12 bits for the MCP 4921
CE = 0 # CE0 or CE1, select SPI device on bus

# setup and open an SPI channel
spi = spidev.SpiDev()
spi.open(0,CE)
spi.max_speed_hz = spi_max_speed

with open('Notes_DAC_Vals.csv', newline='') as csvfile:
    out = csv.reader(csvfile)
    notes = {}
    octave = 1
    count = -1
    names = ("C","Db","D","Eb","E","F","Gb","G","Ab","A","Bb","B")
    for row in out:

        count = count + 1
        if count >= 12:
            count = 0
            octave = octave + 1
        notes[names[count] + str(octave)] = [float(row[0]),int(row[1])]   

notes["A3"][1] = notes["A3"][1]-65
def setOutput(val):
    # lowbyte has all 8 data bits
    # B7, B6, B5, B4, B3, B2, B1, B0
    # D5, D4, D3, D2, D1, D0,  X,  X
    lowByte = val & 0xff
    # highbyte has control and 4 data bits
    # control bits are:
    # B7, B6,   B5, B4,     B3,  B2,  B1,  B0
    # W  ,BUF, !GA, !SHDN,  D9,  D8,  D7,  D6
    # B7=0:write to DAC, B6=0:unbuffered, B5=1:Gain=1X, B4=1:Output is active
    highByte = ((val >> 8) & 0xff) | 0b0 << 7 | 0b0 << 6 | 0b1 << 5 | 0b1 << 4
    # by using spi.xfer2(), the CS is released after each block, transferring the
    # value to the output pin.
    if DEBUG :
        print("Highbyte = {0:08b}".format(highByte))
        print("Lowbyte =  {0:08b}".format(lowByte))
    spi.xfer2([highByte, lowByte])
#spi.writebytes([highByte,lowByte])

try:
    oldDAC = 0
    while True:
        noteIn = input("Enter a note (e.g. C2): ")
        if noteIn in notes:
            DAC = int(notes[noteIn][1])
        elif noteIn == "mute":
            DAC = 0
        else:
            print("Not a valid note")
            DAC = 0
            
        DAC_Vec = list(range(oldDAC, DAC, int(round((DAC-oldDAC)/10))))
        DAC_Vec.append(DAC)
        for n in range(len(DAC_Vec)):
            setOutput(DAC_Vec[n])
            sleep(0.002)

        oldDAC = DAC
except (KeyboardInterrupt, Exception) as e:
    print(e)
    print ("Closing SPI channel")
    setOutput(0)
#    GPIO(cleanup)
    spi.close()

def main():
    pass

if __name__ == '__main__':
    main()

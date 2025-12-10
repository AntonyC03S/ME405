from Line_Class import Line
from pyb import Pin
import sys
import time
import math

line = Line()
line.define_13(Pin.cpu.A0,Pin.cpu.A1,Pin.cpu.A4,
               Pin.cpu.A6,Pin.cpu.A7,Pin.cpu.B0,
               Pin.cpu.B1,Pin.cpu.C0,Pin.cpu.C1,
               Pin.cpu.C2,Pin.cpu.C3,Pin.cpu.C4,
               Pin.cpu.C5)


while True:
    hi = line.update()
    print(hi)
    readings = line.readings()
    for idx,data in enumerate(readings):
        print(f"{idx+2}:", end="")
        data =  int(data)
        string = "#"*data
        print(string)
    print(readings)
    sys.stdout.write("\033[15A")
    time.sleep(0.1)
    print("                   ")
    for idx,data in enumerate(readings):
        print(f"{idx+2}:                      ")
    print("                                                                                                                                                                                                 ")
    sys.stdout.write("\033[15A")

    

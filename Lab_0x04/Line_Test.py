from Line_Class import Line
from pyb import Pin
import sys
import time
import math

line = Line(Pin.cpu.C2, Pin.cpu.C3, Pin.cpu.C0, 
                        Pin.cpu.C1, Pin.cpu.B0, Pin.cpu.A4,
                        Pin.cpu.C4, Pin.cpu.B1)


while True:
    hi = line.update()
    print(hi)
    readings = line.readings()
    for idx,data in enumerate(readings):
        print(f"{idx}:                      ", end="\r")
        print(f"{idx}:", end="")
        data =  int(data*10)
        string = "#"*data
        print(string)
    sys.stdout.write("\033[9A")

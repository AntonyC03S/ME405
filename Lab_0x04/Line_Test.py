from Line_Class import Line
from pyb import Pin

line = Line(Pin.cpu.C2, Pin.cpu.C3, Pin.cpu.C0, 
                        Pin.cpu.C1, Pin.cpu.B0, Pin.cpu.A4,
                        Pin.cpu.C4, Pin.cpu.B1)

while True:
    hi = line.update()
    print(hi)
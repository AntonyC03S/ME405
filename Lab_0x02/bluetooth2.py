from pyb import UART
from time import ticks_ms, ticks_diff, sleep_ms

uart = UART(1, 115200)  # default pins PB6/PB7 on Pyboard
print("Beacon on UART1 (PB6/PB7) @9600")

t0 = ticks_ms()
n = 0
while True:
    if ticks_diff(ticks_ms(), t0) >= 1000:
        uart.write("PING %d\r\n" % n)
        n += 1
        t0 = ticks_ms()
    if uart.any():
        line = uart.readline()
        if line:
            uart.write(b"RX: "); uart.write(line); uart.write(b"\r\n")
    sleep_ms(10)

from pyb import Pin, Timer # type: ignore
from time import ticks_us, ticks_diff, ticks_add   # Use to get dt value in update()
from Encoder_Driver import Encoder


encoder_left  = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)

while True:
    encoder_left.update()
    encoder_right.update()
    print(encoder_left.position, encoder_right.position)
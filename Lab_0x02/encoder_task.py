import gc
import cotask
import task_share
from pyb import Pin, Timer # type: ignore
from time import ticks_us, ticks_diff, ticks_add   # Use to get dt value in update()
from Encoder_Driver import Encoder
from Motor_Driver import Motor

def encoder_task(shares):

    my_share, my_queue = shares
    encoder_left = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
    encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)
    interval = 100_000                          # time interval [us] 
    start    = ticks_us()                       # time of 1st run 
    deadline = ticks_add(start, interval)       # first run deadline 
    now = ticks_us()                          # present time [us] 
    if ticks_diff(deadline, now) <= 0:        # deadline elapsed 
            # Run looping code here; can reference "start" and "now" 
            # variables using ticks_diff() for timestamping actions 
            # of code (like data collection) 
            encoder_left.update() 
            encoder_right.update()
            
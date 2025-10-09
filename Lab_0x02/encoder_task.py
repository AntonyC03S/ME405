import gc
import cotask
import task_share
from pyb import Pin, Timer # type: ignore
from time import ticks_us, ticks_diff, ticks_add   # Use to get dt value in update()
from Encoder_Driver import Encoder
from Motor_Driver import Motor

def encoder_task(shares):
    state = 0
    my_share, my_queue = shares
    encoder_left = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
    encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)
    interval = 100_000                          # time interval [us] 

    while True:
        if state == 0:
            my_share.get()
            if encoder_start == 1:   
                state = 1
                enconder_start = 0
            continue
        elif state == 1:
            start    = ticks_us()                       # time of 1st run 
            deadline = ticks_add(start, interval)       # first run deadline 
            now = ticks_us()                          # present time [us] 
            if ticks_diff(deadline, now) <= 0:        # deadline elapsed 
                    # Run looping code here; can reference "start" and "now" 
                    # variables using ticks_diff() for timestamping actions 
                    # of code (like data collection) 
                    encoder_left.update() 
                    encoder_right.update()
            state = 2
        elif state == 2:
            my_queue.put((encoder_left.get_position(), encoder_right.get_position()))
            state = 1
        else:
            state = 1          
        yield state


if __name__ == "__main__":
     pass
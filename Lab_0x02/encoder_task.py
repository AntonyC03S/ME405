import gc
import cotask
import task_share
from pyb import Pin, Timer # type: ignore
from time import ticks_us, ticks_diff, ticks_add   # Use to get dt value in update()
from Encoder_Driver import Encoder
from Motor_Driver import Motor

def encoder_task(shares):
    state = 0
    encoder_start, motor_speed_left, motor_speed_right, motor_time, done = shares
    encoder_left = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
    encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)
    count = ticks_us()

    while True:
        if state == 0:
            if encoder_start.get() == 1:   
                state = 1
                start = ticks_us()
            else:
                state = 0
        elif state == 1:
            encoder_left.update()
            encoder_right.update()
            if encoder_start.get() == 0:
                state = 0
            else:
                state = 2
        elif state == 2:
            motor_speed_left.put(float(encoder_left.velocity))
            motor_speed_right.put(float(encoder_right.velocity))
            motor_time.put(ticks_diff(start, count))
            if encoder_start.get() == 0:
                state = 0 
            else:
                state = 1     
        yield state


if __name__ == "__main__":
     pass
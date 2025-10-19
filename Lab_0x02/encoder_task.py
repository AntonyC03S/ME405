from pyb import Pin, Timer # type: ignore
from time import ticks_us, ticks_diff, ticks_add   # Use to get dt value in update()
from Encoder_Driver import Encoder

def encoder_task(shares):
    state = 0
    encoder_start, motor_speed_left, motor_speed_right, motor_position_left, motor_position_right, motor_time, done = shares

    # States
    Init = 0
    Stop = 1
    Read = 2
    Send = 3

    while True:
        # State 0 - Init
        # Initialized the motor 
        if state == Init:
            Pin(Pin.cpu.B6,  mode=Pin.ANALOG)     # Set pin modes back to default
            Pin(Pin.cpu.B7,  mode=Pin.ANALOG)
            encoder_left  = Encoder(Timer(4, prescaler = 0, period = 0xFFFF),Pin.cpu.B6,Pin.cpu.B7)
            encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)
            state = Stop


        # State 1 - Not_read
        # Encoder no active. Waiting until it is active
        elif state == Stop:
            count = ticks_us()
            if encoder_start.get() == 1:   
                state = Read
                start = ticks_us()
            else:
                state = Stop

        # State 2 - Reading
        # Encoder is readding data
        elif state == Read:
            encoder_left.update()
            encoder_right.update()
            if encoder_start.get() == 0:
                state = Stop
            else:
                state = Send

        # State 3 - Output data
        # Encoder is giving data out
        elif state == Send:
            motor_speed_left.put(float(encoder_left.velocity))
            motor_speed_right.put(float(encoder_right.velocity))
            motor_position_left.put(float(encoder_left.position))
            motor_position_right.put(float(encoder_right.position))
            motor_time.put(ticks_diff(ticks_us(), start))
            if encoder_start.get() == 0:
                state = Stop
            else:
                state = Read  

        yield state


if __name__ == "__main__":
     pass
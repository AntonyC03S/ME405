from pyb import Pin, Timer, ExtInt # type: ignore
from Motor_Driver import Motor


def motor_task(shares):

    motor_eff, encoder_start, done = shares

    state = 0
    counter = 0


    # States
    Init = 0
    Stop = 1
    Running = 2


    while True:
        # State 0 - Init
        # Initialized the motor 
        if state == Init:
            tim3 = Timer(3, freq=20000)
            motor_left   = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B6,  tim3, 1)  
            motor_right  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, tim3, 2) 
            motor_left.enable()
            motor_right.enable()
            state = Stop

        # State 1 - Stop
        # Disable motor and all motion
        elif state == Stop:
            #motor_left.disable()
            #motor_right.disable()
            eff = int(motor_eff.get())
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            if eff != 0:
                state = Running
                encoder_start.put(1)

        # State 2 - Running
        # Enabling Motor and running an effort
        elif state == Running:
            '''Need to change this later so that we can change each of the effor and so it does not eable every time'''
            eff = int(motor_eff.get())
            motor_left.set_effort(eff)
            motor_right.set_effort(eff)

            counter += 1
            if counter >= 50:
                done.put(1)
                motor_left.set_effort(0)
                motor_right.set_effort(0)
                counter = 0
                state = Stop
            if eff == 0:
                state = Stop
            

        # State Z - State not found
        # State is out of bounds and is reset
        else:
            state = 0

        yield state




if __name__ == "__main__":
    pass
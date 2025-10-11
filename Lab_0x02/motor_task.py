from pyb import Pin, Timer, ExtInt # type: ignore
from Motor_Driver import Motor


def motor_task(shares, enable, effort):
    state = 0


    # States
    Init = 0
    Stop = 1
    Running = 2


    while True:
        # State 0 - Init
        # Initialized the motor 
        if state == Init:
            motor_left   = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B6,  Timer(3, freq=20000), 1)  
            motor_right  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, Timer(3, freq=20000), 2) 
            state = 1

        # State 1 - Stop
        # Disable motor and all motion
        elif state == Stop:
            motor_left.disable()
            motor_right.disable()
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            if enable:
                state = 2

        # State 2 - Running
        # Enabling Motor and running an effort
        elif state == Running:
            '''Need to change this later so that we can change each of the effor and so it does not eable every time'''
            motor_left.enable()
            motor_right.enable()
            motor_left.set_effort(effort)
            motor_right.set_effort(effort)

            if not enable:
                state = 1
            

        # State Z - State not found
        # State is out of bounds and is reset
        else:
            state = 0


        yield state
    
    
    return




if __name__ == "__main__":
    pass
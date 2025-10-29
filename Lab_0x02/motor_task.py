from pyb import Pin, Timer # type: ignore
from Motor_Driver import Motor
from Controller_Class import Controller


def motor_task(shares):

    motor_eff, encoder_start, motor_volt, done, KP, KI, KD,motor_speed_left, motor_speed_right = shares

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
            motor_left   = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)  
            motor_right  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, tim3, 2) 
            controller_left = Controller(KP.get(),KI.get(),KD.get())
            controller_right = Controller(KP.get(),KI.get(),KD.get())
            motor_eff.put(0)
            motor_left.enable()
            motor_right.enable()
            state = Stop

        # State 1 - Stop
        elif state == Stop:
            eff = int(motor_eff.get())
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            if eff != 0:
                state = Running
                encoder_start.put(1)

        # State 2 - Running
        # Enabling Motor and running an effort
        elif state == Running:
            eff = int(motor_eff.get())
            motor_volt.put(1)
            Lgain = controller_left.update(3,motor_speed_left.get())
            Rgain = controller_right.update(3,motor_speed_right.get())
            motor_left.set_effort(eff + Lgain)
            motor_right.set_effort(eff + Rgain)
            counter += 1

            if counter >= 100:
                done.put(1)
                encoder_start.put(0)
                motor_eff.put(0)
                counter = 0
                state = Stop
                
            if eff == 0:
                state = Stop
            

        # State Z - State not found
        # State is out of bounds and is reset
        else:
            state = Stop

        yield state


if __name__ == "__main__":
    pass



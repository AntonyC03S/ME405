from pyb import Pin, Timer # type: ignore
from Motor_Driver import Motor
from Controller_Class import Controller
from Line_Class import Line


def motor_task(shares):

    motor_eff, encoder_start, motor_volt, done, Kp, Ki, Kd, motor_speed_left, motor_speed_right, lspeed, rspeed = shares

    state = 0
    counter = 0


    # States
    Init = 0
    Stop = 1
    Running = 2
    Line = 3


    while True:
        # State 0 - Init
        # Initialized the motor 
        if state == Init:
            tim3 = Timer(3, freq=20000)
            motor_left   = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)  
            motor_right  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, tim3, 2) 
            motor_eff.put(0)
            motor_left.enable()
            motor_right.enable()
            lspeed.put(0)
            rspeed.put(0)
            line = Line(Pin.cpu.C2, Pin.cpu.C3, Pin.cpu.C0, 
                        Pin.cpu.C1, Pin.cpu.B0, Pin.cpu.A4,
                        Pin.cpu.C4, Pin.cpu.B1)
            state = Stop

        # State 1 - Stop
        elif state == Stop:
            eff = int(motor_eff.get())
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            if eff != 0:
                state = Line
                encoder_start.put(1)

        # State 2 - Running
        # Enabling Motor and running an effort
        elif state == Running:
            eff = int(motor_eff.get())
            if counter == 0:
                controller_left = Controller(2.7,20,0.1)
                controller_right = Controller(2,19,0.1)
                motor_left.set_effort(eff)
                motor_right.set_effort(eff)
            else:
                Lgain = controller_left.update(15,lspeed.get())
                Rgain = controller_right.update(15,rspeed.get())
                Lnew = eff + Lgain
                Rnew = eff + Rgain
                motor_left.set_effort(Lnew)
                motor_right.set_effort(Rnew)
            motor_volt.put(1)

            counter += 1

            if counter >= 100:
                done.put(1)
                encoder_start.put(0)
                motor_eff.put(0)
                counter = 0
                state = Stop
                
            if eff == 0:
                state = Stop
            
        elif state == Line:
            eff = int(motor_eff.get())
            if counter == 0:
                controller_left = Controller(2.7,20,0.1)
                controller_right = Controller(2,19,0.1)
                motor_left.set_effort(eff)
                motor_right.set_effort(eff)
            else:
                centroid = line.update()
                if centroid <= 0:
                    Lgain = controller_left.update(15 + centroid,lspeed.get())
                    Rgain = controller_right.update(15 - centroid,rspeed.get())
                    Lnew = eff + Lgain
                    Rnew = eff + Rgain
                    motor_left.set_effort(Lnew)
                    motor_right.set_effort(Rnew)
                else:
                    Lgain = controller_left.update(15 - centroid,lspeed.get())
                    Rgain = controller_right.update(15 + centroid,rspeed.get())
                    Lnew = eff + Lgain
                    Rnew = eff + Rgain
                    motor_left.set_effort(Lnew)
                    motor_right.set_effort(Rnew)

        else:
            state = Stop
    

        yield state


if __name__ == "__main__":
    pass



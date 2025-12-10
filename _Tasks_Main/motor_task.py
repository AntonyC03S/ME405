from pyb import Pin, Timer # type: ignore
from Motor_Driver import Motor
from Controller_Class import Controller
from Line_Class import Line


def motor_task(shares):

    motor_eff, encoder_start, L_volt, R_volt, done, Kp, Ki, Kd,lspeed, rspeed,s,a,data_sharing = shares

    state = 0
    counter = 0
    checkpoint = 0

    # States
    Init = 0
    Stop = 1
    Running = 2
    Line_Running = 3
    PID_Tuning = 4
    Backward = 5
    Turn = 6

    while True:
        # State 0 - Init
        # Initialized the motor 
        if state == Init:
            tim3 = Timer(3, freq=20000)
            # motor_left   = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)  #Pink bot
            # motor_right  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B14, tim3, 2)     
            motor_left   = Motor(Pin.cpu.C8, Pin.cpu.A10,  Pin.cpu.B2,  tim3, 3)  
            motor_right  = Motor(Pin.cpu.C9, Pin.cpu.B12, Pin.cpu.B14, tim3, 4) 
            motor_eff.put(0)
            motor_left.enable()
            motor_right.enable()
            lspeed.put(0)
            rspeed.put(0)
            line = Line()
            # line.define_8(Pin.cpu.C2, Pin.cpu.C3, Pin.cpu.C0,       #Pink bot
            #             Pin.cpu.C1, Pin.cpu.B0, Pin.cpu.A4,
            #             Pin.cpu.C4, Pin.cpu.B1)
            line.define_13(Pin.cpu.A0,Pin.cpu.A1,Pin.cpu.A4,
               Pin.cpu.A6,Pin.cpu.A7,Pin.cpu.B0,
               Pin.cpu.B1,Pin.cpu.C0,Pin.cpu.C1,
               Pin.cpu.C2,Pin.cpu.C3,Pin.cpu.C4,
               Pin.cpu.C5)
            state = Stop
            L_volt.put(0)
            R_volt.put(0)

        # State 1 - Stop
        elif state == Stop:
            eff = int(motor_eff.get())
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            PID_data = data_sharing.get() 
            if eff != 0:
                if PID_data == 0:
                    state = Line_Running
                else:
                    state = PID_Tuning
                encoder_start.put(1)

        # State 2 - Running
        # Enabling Motor and running an effort
        elif state == Running:
            eff = int(motor_eff.get())
            if counter == 0:
                # controller_left = Controller(2.7,20,0.1)
                # controller_right = Controller(2,19,0.1)
                controller_left = Controller(1.5,12.5,0.1)
                controller_right = Controller(1.6,12.5,0.1)
                motor_left.set_effort(eff)
                motor_right.set_effort(eff)
            else:
                Lgain = controller_left.update(15,lspeed.get())
                Rgain = controller_right.update(15,rspeed.get())
                Lnew = eff + Lgain
                Rnew = eff + Rgain
                motor_left.set_effort(Lnew)
                motor_right.set_effort(Rnew)

            counter += 1

            if counter >= 100:
                done.put(1)
                encoder_start.put(0)
                motor_eff.put(0)
                counter = 0
                state = Stop
                
            if eff == 0:
                state = Stop
            
        # State 3 - Running and Following a line
        # Enabling Motor, Encoder, and Line Sensor
        elif state == Line_Running:
            eff = int(motor_eff.get())
            if counter == 0:
                # controller_left = Controller(2.7,20,0.1)
                # controller_right = Controller(2,19,0.1)
                # controller_left = Controller(2.7,20,0.1)
                # controller_right = Controller(2,19,0.1)
                controller_left = Controller(1.5,12.5,0.1)
                controller_right = Controller(1.6,12.5,0.1)
                controller_line = Controller(1.2,0,0)
                motor_left.set_effort(eff)
                motor_right.set_effort(eff)
                u = 7.2 * (eff / 100.0)
                L_volt.put(u)
                R_volt.put(u)
                # state  = Turn
                # hi = a.get()
            else:
                basespeed = 5
                if s.get() >= 30000:
                    if checkpoint == 0:
                        state = Backward 
                        
                centroid = line.update()
                error_line = centroid - 8
                Line_gain = controller_line.update(0, error_line)
                vL_set = basespeed - Line_gain
                vR_set = basespeed + Line_gain
                vL_set = max(min(vL_set, 100), -100)
                vR_set = max(min(vR_set, 100), -100)
                Lgain = controller_left.update(vL_set,lspeed.get())
                Rgain = controller_right.update(vR_set,rspeed.get())
                motor_left.set_effort(Lgain)
                motor_right.set_effort(Rgain)
                L_volt.put(7.2 * (Lgain / 100.0))
                R_volt.put(7.2 * (Rgain / 100.0))
                
            counter += 1

            if counter >= 1000:
                done.put(1)
                encoder_start.put(0)
                motor_eff.put(0)
                counter = 0
                state = Stop
                
            if eff == 0:
                state = Stop

        # State 5 - Backward
        elif state == Backward:
            checkpoint = 1
            basespeed = -5
            centroid = line.update()
            error_line = centroid - 8
            Line_gain = controller_line.update(0, error_line)
            vL_set = basespeed 
            vR_set = basespeed 
            vL_set = max(min(vL_set, 100), -100)
            vR_set = max(min(vR_set, 100), -100)
            Lgain = controller_left.update(vL_set,lspeed.get())
            Rgain = controller_right.update(vR_set,rspeed.get())
            motor_left.set_effort(Lgain)
            motor_right.set_effort(Rgain)
            L_volt.put(7.2 * (Lgain / 100.0))
            R_volt.put(7.2 * (Rgain / 100.0))
            
            counter += 1

            if s.get() <=25000:
                basespeed = 5
                state = Turn
                hi = a.get()

            if counter >= 1000:
                done.put(1)
                encoder_start.put(0)
                motor_eff.put(0)
                counter = 0
                state = Stop

        # State 6 - Turn
        elif state == Turn:
            basespeed = 5
            vL_set = -basespeed
            vR_set = basespeed
            vL_set = max(min(vL_set, 100), -100)
            vR_set = max(min(vR_set, 100), -100)
            Lgain = controller_left.update(vL_set,lspeed.get())
            Rgain = controller_right.update(vR_set,rspeed.get())
            motor_left.set_effort(Lgain)
            motor_right.set_effort(Rgain)
            L_volt.put(7.2 * (Lgain / 100.0))
            R_volt.put(7.2 * (Rgain / 100.0))
            
            counter += 1
            deltaa = abs(a.get() - abs(hi))

            if deltaa >= 222:
                state = Line_Running


            if counter >= 1000:
                done.put(1)
                encoder_start.put(0)
                motor_eff.put(0)
                counter = 0
                state = Stop
            





        # State 4 - PID Tuning
        # Enabling Motor and running an effort
        elif state == PID_Tuning:
            eff = int(motor_eff.get())
            if counter == 0:
                # PID_side_split = PID_data.split("-")
                # PID_left_split = PID_side_split[0].split("*") 
                # PID_right_split = PID_side_split[1].split("*") 
                # controller_left = Controller(2.7,20,0.1)
                # controller_right = Controller(2,19,0.1)
                controller_left = Controller(1.5,12.5,0.1)
                controller_right = Controller(1.6,12.5,0.1)
                motor_left.set_effort(eff)
                motor_right.set_effort(eff)
            else:
                Lgain = controller_left.update(15,lspeed.get())
                Rgain = controller_right.update(15,rspeed.get())
                Lnew = eff + Lgain
                Rnew = eff + Rgain
                motor_left.set_effort(Lnew)
                motor_right.set_effort(Rnew)

            counter += 1

            if counter >= 50:
                done.put(1)
                encoder_start.put(0)
                motor_eff.put(0)
                counter = 0
                state = Stop
            if eff == 0:
                state = Stop






        # State X - Error State
        else:
            state = Stop
    

        yield state


if __name__ == "__main__":
    pass



from pyb import Pin, Timer # type: ignore
from Motor_Driver import Motor
from Controller_Class import Controller
from Line_Class import Line


def motor_task(shares):

    motor_eff, encoder_start, L_volt, R_volt, done, Kp, Ki, Kd,lspeed, rspeed,s,a,data_sharing = shares

    state = 0
    counter = 0
    checkpoint = 0
    buffer = 0

    # States
    Init = 0
    Stop = 1
    Running = 2
    Line_Running = 3
    PID_Tuning = 4
    Backward = 5
    Turn = 6
    Time_tial = 7

    while True:
        # State 0 - Init
        # Initialized the motor 
        if state == Init:
            tim3 = Timer(3, freq=20000)     
            motor_left   = Motor(Pin.cpu.C8, Pin.cpu.A10,  Pin.cpu.B2,  tim3, 3)  
            motor_right  = Motor(Pin.cpu.C9, Pin.cpu.B12, Pin.cpu.B14, tim3, 4) 
            motor_eff.put(0)
            motor_left.enable()
            motor_right.enable()
            lspeed.put(0)
            rspeed.put(0)
            line = Line()
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
            PID_data = 0
            if eff != 0:
                if PID_data == 0:
                    state = Line_Running
                elif PID_data == 9:
                    state = Time_tial
                    time_stage = -1
                else:
                    state = PID_Tuning
                encoder_start.put(1)

        # State 2 - Running
        # Enabling Motor and running an effort
        elif state == Running:
            eff = int(motor_eff.get())
            if counter == 0:
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
                controller_left = Controller(1.5,12.5,0.1)
                controller_right = Controller(1.3,11,0.1)
                controller_line = Controller(0.5,0,0.05) #1.35
                motor_left.set_effort(eff)
                motor_right.set_effort(eff)
                switch = Pin.cpu.C10   
                switch.init(Pin.IN, Pin.PULL_UP)
                u = 7.2 * (eff / 100.0)
                L_volt.put(u)
                R_volt.put(u)
                subcheck = 0
                frist = 0
                set_time = 1000000000000000000
            else:
                basespeed = 6
                turn_count = 0
                if s.get() >= set_time+32000:
                    if subcheck == 3:
                        done.put(1)
                        encoder_start.put(0)
                        motor_eff.put(0)
                        counter = 0
                        state = Stop
                elif s.get() >= set_time+19000:
                    if subcheck == 2:
                        state = Turn
                        hi = a.get()

                elif s.get() >= set_time+10000:
                    if subcheck == 1:
                        state = Turn
                        hi = a.get()
                elif s.get() >= set_time+10: # forward from the bump sensor
                    if checkpoint == 5 and subcheck == 0:
                        state = Turn
                        hi = a.get()
                elif s.get() >= 102800: 
                    if checkpoint == 3:
                        state = Turn
                elif s.get() >= 86000:
                    if checkpoint == 2:
                        state = Turn
                        hi = a.get()
                        last_a = hi
                        controller_line._KP  = 0.0
                        controller_line._KD  = 0.0
                elif s.get() >= 77000:
                    controller_line._KP  = 0.5
                    controller_line._KD  = 0.03
                elif s.get() >= 67000:
                    controller_line._KP  = 0.0
                    controller_line._KD  = 0

                elif s.get() >= 31000:
                    if checkpoint == 0:
                        checkpoint = 1
                        state = Backward
                        frist = 1
                
                if frist == 0:
                    robot_line_center = 5.5
                    if s.get() >= 26500:
                        robot_line_center = 8
                        controller_line._KP  = 0
                else:
                    robot_line_center = 8
                        
                centroid = line.update()
                error_line = centroid - robot_line_center
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
            if eff == 0:
                state = Stop

        # State 5 - Backward
        elif state == Backward:
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
                if checkpoint == 1:
                    basespeed = 5
                    state = Turn
                    hi = a.get()
            if switch.value() == 1:
                set_time = s.get()
                state = Line_Running
                checkpoint = 5


        # State 6 - Turn
        elif state == Turn:
            basespeed = 2.5
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
            turn_count += 1
            deltaa = hi - a.get()

            if checkpoint == 1:
                if deltaa >= 120:
                    state = Line_Running
                    checkpoint = 2
                    controller_line._KP  = 0.55
                    controller_line._KD  = 0.03

            elif checkpoint == 2:
                if turn_count >= 5: 
                    state = Line_Running
                    checkpoint = 3
            elif checkpoint == 3:
                if turn_count >= 25: #104500
                    state = Backward
            elif checkpoint == 5:
                if subcheck == 0:
                    if turn_count >= 25:
                        subcheck += 1
                        state = Line_Running
                else:
                    if turn_count >= 25:
                        subcheck += 1
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
                controller_left = Controller(1.5,12.5,0.1)
                controller_right = Controller(1.6,12.5,0.1)
                motor_left.set_effort(eff)
                motor_right.set_effort(eff)
            else:
                Lgain = controller_left.update(25,lspeed.get())
                Rgain = controller_right.update(-25,rspeed.get())
                Lnew = eff + Lgain
                Rnew = eff + Rgain
                motor_left.set_effort(Lnew)
                motor_right.set_effort(Rnew)

            counter += 1

            if counter >= 10:
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



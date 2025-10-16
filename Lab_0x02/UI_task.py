import pyb # type: ignore



def UI_task(shares):
    state = 0
    ser = pyb.USB_VCP()
    motor_eff, results, done, motor_speed_left, motor_speed_right, motor_time, encoder_start = shares

    # States
    Init = 0
    Not_read = 1
    Read = 2
    Output_data = 3

    while True:

        if state == 0:
            print("Select number from 0-9 to set motor speed.")
            Print = False
            state = 1


        elif state == 1:
            if ser.any():
                char_in = ser.read(1).decode()
                if char_in in '0123456789':
                    speed = int(char_in) * 10
                    motor_eff.put(speed)
                    print(f"Motor speed set to {speed}%")
                    state = 2
                else:
                    print("Invalid input. Please enter a number from 0-9.")
                    state = 1

        elif state == 2:
            if  done.get() == 1:
                motor_eff.put(0)
                print("Task complete.")
                state = 3
                encoder_start.put(0)
                done.put(0)
            else:
                state = 2


        elif state == 3:
            if not Print:
                print("Time (us)\tLeft Speed (units/s)\tRight Speed (units/s)")
                Print = True
            # Drain any available triplets in lockstep
            while motor_speed_left.any() and motor_speed_right.any() and motor_time.any():
                t = motor_time.get()             
                l = float(motor_speed_left.get())     
                r = float(motor_speed_right.get())    
                print("{}\t{:.2f}\t{:.2f}".format(t, l, r))
                state = 3
        yield state

if __name__ == "__main__":
    pass
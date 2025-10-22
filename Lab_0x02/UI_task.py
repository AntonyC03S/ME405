from pyb import Pin,UART # type: ignore
import math
from time import sleep_ms



def UI_task(shares):
    state = 0
    # ser = pyb.USB_VCP()
    motor_eff, results, done, motor_speed_left, motor_speed_right, motor_time, encoder_start = shares
    bluetooth = UART(1, 115200)
    Pin(Pin.cpu.A9,  mode=Pin.ALT, alt=7) # Set pin modes to UART matching column 7 in alt. fcn. table
    Pin(Pin.cpu.A10, mode=Pin.ALT, alt=7)
    start = False

    # States
    Init = 0
    Not_read = 1
    Read = 2
    Output_data = 3

    while True:
        if state == 0:
            if not start and bluetooth.any():
                print("hi")
                line = bluetooth.readline()
                if not line:
                    sleep_ms(10)
                    continue
                try:
                    cmd = line.decode().strip()
                except Exception:
                    cmd = ''

                if cmd.lower() == 'c':
                    # begin streaming all collected rows
                    start = True
            if start == True:
                print("Testing starting.")
                speed = 50
                motor_eff.put(speed)
                Print = False
                state = 2


        elif state == 1:
            pass
            # if ser.any():
            #     char_in = ser.read(1).decode()
            #     if char_in in '0123456789':
            #         speed = int(char_in) * 10
            #         motor_eff.put(speed)
            #         print(f"Motor speed set to {speed}%")
            #         state = 2
            #     else:
            #         print("Invalid input. Please enter a number from 0-9.")
            #         state = 1

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
            pass
            # if not Print:
            #     print("Time (s)\tLeft Speed (rad/s)\tRight Speed (rad/s)")
            #     Print = True
            # # Drain any available triplets in lockstep
            # while motor_speed_left.any() and motor_speed_right.any():
            #     t = motor_time.get() / 1_000_000
            #     l = motor_speed_left.get() 
            #     r = motor_speed_right.get() * -1
            #     print("{}\t{}\t{}".format(t, l, r))
            #     state = 3
        yield state

if __name__ == "__main__":
    pass
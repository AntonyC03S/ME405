import pyb
import cotask
import task_share
import keyboard

def UI_task(shares):
    state = 0
    ser = pyb.USB_VCP()
    my_share, my_queue = shares
    while True:
        if state == 0:
            print("Select number from 0-9 to set motor speed.")
            state = 1
        elif state == 1:
            if ser.any():
                char_in = ser.read(1).decode()
                if char_in in '0123456789':
                    speed = int(char_in) * 10
                    my_share.put(speed)
                    print(f"Motor speed set to {speed}%")
                else:
                    print("Invalid input. Please enter a number from 0-9.")
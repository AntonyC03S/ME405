from Bluetooth_Driver import Bluetooth
from pyb import Pin, UART
from time import sleep_ms


def data_task(shares):
    state = 0
    motor_volt, motor_speed_left, motor_speed_right, motor_position_left, motor_position_right, motor_time, results, done = shares
    rows = []
    # States
    Init = 0
    Collect = 1
    Send = 2
    sending = False
    send_index = 0

    def send_line(s):
    # ensure CRLF termination
        if not s.endswith('\n'):
            s = s + '\r\n'   
        bluetooth.write(s)


    while True:
        # State 0 - Init
        if state == Init:
            bluetooth = UART(1, 115200)
            Pin(Pin.cpu.B6,  mode=Pin.ANALOG)     # Set pin modes back to default
            Pin(Pin.cpu.B7,  mode=Pin.ANALOG)
            # Configure the selected pins in coordination with the alternate function table
            Pin(Pin.cpu.A9,  mode=Pin.ALT, alt=7) # Set pin modes to UART matching column 7 in alt. fcn. table
            Pin(Pin.cpu.A10, mode=Pin.ALT, alt=7)
            state = Collect


        # State 1 - Collect
        elif state == Collect:
            if (motor_speed_left.any() and motor_speed_right.any() and motor_time.any()
                and motor_position_left.any() and motor_position_right.any() and motor_volt.any()):
                
                ls = motor_speed_left.get()
                rs = motor_speed_right.get() * -1
                lp = motor_position_left.get()
                rp = motor_position_right.get()
                v  = motor_volt.get()
                t  = motor_time.get()/  1_000_000

                rows.append((t, lp, rp, ls, rs, v))
            if done.get() == 1:
                state = Send



                
        # State 2 - Send
        # 
        elif state == Send:
            if not sending and bluetooth.any():
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
                    sending = True
                    send_index = 0

            if sending:
                if send_index < len(rows):
                    t, left_pos, right_pos, left_speed, right_speed, volt = rows[send_index]
                    send_line('{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f}'.format(t, left_pos, right_pos, left_speed, right_speed, volt))
                    send_index += 1
                else:
                    send_line('END')
                    rows.clear()
                    sending = False
                    send_index = 0
                    print("All data sent")
                    state = Collect
        else:
            state = 0


        yield state




if __name__ == "__main__":
    pass
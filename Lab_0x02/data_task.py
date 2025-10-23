
from pyb import UART
from time import sleep_ms

def data_task(shares):
    state = 0
    (motor_volt,
     motor_speed_left, motor_speed_right,
     motor_position_left, motor_position_right,
     motor_time,
     results, done) = shares

    # States
    Init = 0
    Collect = 1
    Send = 2

    uart = None

    def send_line(s):
        # ensure CRLF and write as bytes
        if not s.endswith('\n'):
            s = s + '\r\n'
        uart.write(s.encode())

    while True:
        if state == Init:
            uart = UART(1, 115200)
            while uart.any():
                uart.read()
            state = Collect
            yield state

        elif state == Collect:
            wrote_any = False
            while (motor_speed_left.any() and motor_speed_right.any() and motor_time.any()
                   and motor_position_left.any() and motor_position_right.any()):
                ls = motor_speed_left.get()
                rs = -motor_speed_right.get()  
                lp = motor_position_left.get()
                rp = -motor_position_right.get()
                v  = motor_volt.get()          
                t_us = motor_time.get()
                t = t_us / 1_000_000.0         


                send_line('{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f}'.format(
                    t, lp, rp, ls, rs, v
                ))
                wrote_any = True

            if done.get() >= 1 and not (motor_speed_left.any() or motor_speed_right.any()
                                        or motor_position_left.any() or motor_position_right.any()
                                        or motor_time.any()):
                state = Send

            if not wrote_any:
                sleep_ms(1)
            yield state
        elif state == Send:
            send_line('END')
            done.put(0)
            state = Collect
            yield state

        else:
            state = Init
            yield state

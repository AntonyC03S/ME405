# from Bluetooth_Driver import Bluetooth
# from pyb import Pin, UART
# from time import sleep_ms


# def data_task(shares):
#     state = 0
#     motor_volt, motor_speed_left, motor_speed_right, motor_position_left, motor_position_right, motor_time, results, done = shares
#     #rows = []
#     rows_time_voltage = []
#     rows_voltage = []
#     rows_speed = []
#     rows_position = []
#     # States
#     Init = 0
#     Collect = 1
#     Send = 2
#     sending = False
#     send_index = 0

#     def send_line(s):
#     # ensure CRLF termination
#         if not s.endswith('\n'):
#             s = s + '\r\n'   
#         bluetooth.write(s)


#     while True:
#         # State 0 - Init
#         if state == Init:
#             # Configure the selected pins in coordination with the alternate function table
#             state = Collect


#         # State 1 - Collect
#         elif state == Collect:
#             if (motor_speed_left.any() and motor_speed_right.any() and motor_time.any()
#                 and motor_position_left.any() and motor_position_right.any()):
                
#                 ls = motor_speed_left.get()
#                 rs = motor_speed_right.get() * -1
#                 lp = motor_position_left.get()
#                 rp = motor_position_right.get()
#                 v  = motor_volt.get()
#                 t  = motor_time.get()

#                 #rows.append((t, lp, rp, ls, rs, v))
#                 print(t)
#                 rows_time_voltage.append(t)
#                 rows_voltage.append(v)
#                 rows_speed.append((ls, rs))
#                 rows_position.append((lp, rp))
#             if done.get() >= 1:
#                 state = Send
#                 bluetooth = UART(1, 115200)



                
#         # State 2 - Send
#         # 
#         elif state == Send:
#             # if not sending and bluetooth.any():
#             #     line = bluetooth.readline()
#             #     if not line:
#             #         sleep_ms(10)
#             #         continue
#             #     try:
#             #         cmd = line.decode().strip()
#             #     except Exception:
#             #         cmd = ''

#             #     if cmd.lower() == 'c':
#             #         # begin streaming all collected rows
#             #         sending = True
#             #         send_index = 0

#             # if sending:
#                 if send_index < len(rows_time_voltage):
#                     t = rows_time_voltage[send_index]
#                     volt = rows_voltage[send_index]
#                     left_pos, right_pos= rows_position[send_index]
#                     left_speed, right_speed = rows_speed[send_index]

#                     send_line('{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f}'.format(t, left_pos, right_pos, left_speed, right_speed, volt))
#                     send_index += 1
#                 else:
#                     send_line('END')
#                     rows_time_voltage.clear()
#                     rows_position.clear()
#                     rows_speed.clear()
#                     rows_voltage.clear()
#                     sending = False
#                     send_index = 0
#                     print("All data sent")
#                     state = Collect
#         else:
#             state = 0


#         yield state




# if __name__ == "__main__":
#     pass


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

    # Open the Bluetooth UART once and reuse it
    uart = None

    def send_line(s):
        # ensure CRLF and write as bytes
        if not s.endswith('\n'):
            s = s + '\r\n'
        uart.write(s.encode())

    while True:
        # ---------------------------------------------------------
        # State 0 - Init
        # ---------------------------------------------------------
        if state == Init:
            uart = UART(1, 115200)
            # flush any junk
            while uart.any():
                uart.read()
            state = Collect
            yield state

        # ---------------------------------------------------------
        # State 1 - Collect (stream rows LIVE; no big buffers)
        # ---------------------------------------------------------
        elif state == Collect:
            # drain any COMPLETE samples in lockstep and stream immediately
            wrote_any = False
            while (motor_speed_left.any() and motor_speed_right.any() and motor_time.any()
                   and motor_position_left.any() and motor_position_right.any()):
                ls = motor_speed_left.get()
                rs = -motor_speed_right.get()  # your original negation
                lp = motor_position_left.get()
                rp = motor_position_right.get()
                v  = motor_volt.get()          # Share: just get latest
                t_us = motor_time.get()
                t = t_us / 1_000_000.0         # seconds

                # format one CSV row (same 6 floats your PC expects)
                send_line('{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f}'.format(
                    t, lp, rp, ls, rs, v
                ))
                wrote_any = True

            # if run finished and all queues are empty, go send END
            if done.get() >= 1 and not (motor_speed_left.any() or motor_speed_right.any()
                                        or motor_position_left.any() or motor_position_right.any()
                                        or motor_time.any()):
                state = Send

            if not wrote_any:
                sleep_ms(1)
            yield state

        # ---------------------------------------------------------
        # State 2 - Send END marker, then go back to Collect
        # ---------------------------------------------------------
        elif state == Send:
            send_line('END')
            # reset the latch so next run can stream again
            done.put(0)
            state = Collect
            yield state

        else:
            # safety fallback
            state = Init
            yield state

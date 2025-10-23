from pyb import UART
from time import sleep_ms

def UI_task(shares):
    state = 0
    motor_eff, results, done, motor_speed_left, motor_speed_right, motor_time, encoder_start = shares
    start = False
    sleep_period = 100
    test_effort = 0
    test_done = 0

    # UART1 on PB6 (TX) / PB7 (RX)
    bluetooth = UART(1, 115200)

    # Clear any junk already in the buffer
    while bluetooth.any():
        bluetooth.read()

    buf = bytearray()

    while True:
        if state == 0:
            if not start and bluetooth.any():
                chunk = bluetooth.read()
                if chunk:
                    buf += chunk
                    while True:
                        end_idx = -1
                        sep_len = 0
                        for sep in (b"\r\n", b"\n", b"\r"):
                            i = buf.find(sep)
                            if i != -1:
                                end_idx = i
                                sep_len = len(sep)
                                break
                        if end_idx == -1:
                            break
                        line = bytes(buf[:end_idx])
                        buf[:] = buf[end_idx + sep_len:]

                        # Decode safely without keyword arguments
                        try:
                            cmd = line.decode().strip()
                        except UnicodeError:
                            cmd = "".join(chr(b) for b in line if 32 <= b < 127).strip()
                        if not cmd:
                            continue
                        if cmd.lower().startswith("c"):
                            start = True
                            state = 2
                            break
            yield state

        elif state == 2:
            if test_done >= 12:
                motor_eff.put(0)
                print("Task complete.")
                encoder_start.put(0)
                done.put(0)
                state = 3
            else:
                if sleep_period >= 25:
                    print(f"Testing {test_effort}% effort")
                    motor_eff.put(test_effort)
                    encoder_start.put(0)
                    motor_speed_left.clear()
                    motor_speed_right.clear()
                    motor_time.clear()
                    sleep_period = 0
                    test_effort += 10
                    test_done += 1
                else:
                    sleep_period += 1
            yield state

        elif state == 3:
            yield state

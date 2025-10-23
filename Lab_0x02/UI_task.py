from pyb import UART
from time import sleep_ms

def UI_task(shares):
    state = 0
    motor_eff, results, done, motor_speed_left, motor_speed_right, motor_time, encoder_start = shares
    start = False

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
                            test(motor_eff)
                            state = 2
                            break
            yield state

        elif state == 2:
            if done.get() == 1:
                motor_eff.put(0)
                print("Task complete.")
                encoder_start.put(0)
                done.put(0)
                state = 3
            yield state

        elif state == 3:
            yield state


def test(motor_eff):
    print("Testing starting.")
    for i in range(0,10):
        i *= 10
        print(f"Testing {i}% effort")
        motor_eff.put(i)
        sleep_ms(1000)
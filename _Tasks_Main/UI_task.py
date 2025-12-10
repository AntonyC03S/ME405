from pyb import UART, ExtInt, Pin  # type: ignore
from time import sleep_ms
from gc import collect

def UI_task(shares):
    button = []
    def button_callback(button):
        def button_LED_toggle(the_pin):
            button.append(0)
    button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_callback(button))
    motor_eff, results, done, motor_speed_left, motor_speed_right, motor_time, encoder_start, Kp, Ki, Kd,data_sharing = shares
    state = 0
    start = False
    sleep_period = 100
    test_effort = 0
    test_done = 0
    Pid = False

    # UART1 on PB6 (TX) / PB7 (RX)
    bluetooth = UART(1, 115200)

    # Clear any junk already in the buffer
    while bluetooth.any():
        bluetooth.read()

    buf = bytearray()

    while True:
        if state == 0:
            mode = input("Enable Bluetooth? Yes or No")

            #<--       Bluetooth              -->
            if "no" == "yes":
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
                            elif cmd.lower().startswith("1"):
                                cmd_split = cmd.split("_")
                                PID_list = cmd_split[1:4]
                                kp = float(PID_list[0])
                                ki = float(PID_list[1])
                                kd = float(PID_list[2])
                                Kp.put(float(kp))
                                Ki.put(float(ki))
                                Kd.put(float(kd))
                                state = 2
                                Pid = True
                                break
                            elif cmd.lower().startswith("2"):
                                cmd_split = cmd.split("_")
                                data_sharing.put(cmd_split[1])
                                state = 2
                                Pid = True
                                break

                #<--       Direct Input              -->
            else:
                # input_P_gain = input("Input P gain: ")
                # input_I_gain = input("Input I gain: ")
                # input_D_gain = input("Input D gain: ")
                # Kp.put(float(input_P_gain))
                # Ki.put(float(input_I_gain))
                # Kd.put(float(input_D_gain))
                state = 2
                Pid = True
            yield state

        elif state == 2:
            if Pid == True:
                motor_eff.put(5)
                state = 3
                
            if start == True:
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
            if len(button) != 0:
                state == 4
                print("button")
            collect()
            yield state

        elif state == 4:
            print("button act")
            motor_eff.put(0)
            encoder_start.put(0)
            done.put(0)
            state = 3
            yield state

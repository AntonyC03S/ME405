from pyb import Pin, Timer, ExtInt # type: ignore


def data_task(shares):
    state = 0
    motor_volt, motor_speed_left, motor_speed_right, motor_time, results, done = shares

    rows = []
    # States
    Init = 0
    Collect = 1
    Send = 2


    while True:
        if state == Init:
            pass
        #     if motor_speed_left.any() and motor_speed_right.any() and motor_time.any():
        #         state = Collect

        # elif state == Collect:
        #     while motor_speed_left.any() and motor_speed_right.any() and motor_time.any():
        #         left = motor_speed_left.get()
        #         right = motor_speed_right.get()
        #         t = motor_time.get()
        #         rows.append((t, left, right))
        #     if done.get() == 1:
        #         state = Send
        # # State 2 - Send
        # # 
        # elif state == Send:
        #     results.put(rows)
        #     rows = []
        #     done.put(0)
        #     state = Init   
        

        # # State Z - State not found
        # # State is out of bounds and is reset
        # else:
        #     state = 0


        yield state




if __name__ == "__main__":
    pass
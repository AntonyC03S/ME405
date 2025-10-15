from pyb import Pin, Timer, ExtInt # type: ignore


def data_task(shares):
    state = 0
    motor_volt, motor_speed_left, motor_speed_right, motor_position_left, motor_position_right, motor_time, results, done = shares

    rows = []
    # States
    Init = 0
    Collect = 1
    Send = 2


    while True:
        # State 0 - Init
        # 
        if state == Init:
            pass
            if motor_speed_left.any() or motor_speed_right.any() or motor_time.any():
                state = Collect


        # State 1 - Collect
        # 
        elif state == Collect:
            while motor_speed_left.any() and motor_speed_right.any() and motor_time.any() and motor_position_left.any() and motor_position_right.any() and motor_volt.any():
                left_speed = motor_speed_left.get()
                right_speed = motor_speed_right.get()
                left_position = motor_position_left.get()
                right_position = motor_position_right.get()
                volt = motor_volt.get()
                time = motor_time.get()
                rows.append((time, left_position, right_position, left_speed, right_speed, volt))
            if done.get() == 1:
                state = Send
                
        # State 2 - Send
        # 
        elif state == Send:
            results.put(rows)
            rows = []
            done.put(0)
            state = Init   
        

        # State Z - State not found
        # State is out of bounds and is reset
        else:
            state = 0


        yield state




if __name__ == "__main__":
    pass
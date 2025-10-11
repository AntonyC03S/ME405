from pyb import Pin, Timer, ExtInt # type: ignore


def data_task(shares):
    state = 0


    # States
    Init = 0
    Collect = 1
    Send = 2


    while True:
        # State 0 - Init
        # IDK
        if state == Init:
            pass

        # State 1 - Collect
        # IDK
        elif state == Collect:
            pass

        # State 2 - Send
        # 
        elif state == Send:
            pass

            

        # State Z - State not found
        # State is out of bounds and is reset
        else:
            state = 0


        yield state
    
    
    return




if __name__ == "__main__":
    pass
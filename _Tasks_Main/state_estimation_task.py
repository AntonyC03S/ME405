from pyb import Pin, Timer # type: ignore
from State_Estimation_class import State_Estimation

def encoder_task(shares):
    state = 0

    # States
    Init = 0
    Stop = 1
    Read = 2
    Send = 3

    while True:
        if state == Init:
            pass

        elif state == Stop:
            pass

        elif state == Read:
            pass

        elif state == Send:
            pass

        yield state


if __name__ == "__main__":
     pass
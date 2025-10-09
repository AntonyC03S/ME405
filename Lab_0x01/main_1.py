from pyb import Pin, Timer, ExtInt # type: ignore
from time import ticks_us, ticks_diff, ticks_add   # Use to get dt value in update()
from Encoder_Driver import Encoder
from Motor_Driver import Motor

button_test = 0
def button_LED_toggle(the_pin):
    global button_test
    button_test +=1
    if button_test >= 8:
        button_test = 0


def main():
    button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_LED_toggle)

    interval = 100_000                          # time interval [us] 
    start    = ticks_us()                       # time of 1st run 
    # Run initialization code here 
    encoder_left = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
    encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)
    motor_left  = Motor(Pin.cpu.A6, Pin.cpu.C7, Pin.cpu.B6, Timer(3, freq=20000), 1) #
    motor_right  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, Timer(3, freq=20000), 2) #

    deadline = ticks_add(start, interval)       # first run deadline 
    while True: 
        # Test 1 
        if button_test == 0:
            motor_left.enable()
            motor_right.enable()
        elif button_test == 1:
            motor_left.set_effort(25)
            motor_right.set_effort(-25)
        elif button_test == 2:
            motor_left.set_effort(50)
            motor_right.set_effort(-50)
        elif button_test == 3:
            motor_left.set_effort(23)
            motor_right.set_effort(-70)
        elif button_test == 4:
            motor_left.set_effort(-23)
            motor_right.set_effort(78)
        elif button_test == 5:
            motor_left.set_effort(-25)
            motor_right.set_effort(-25)
        elif button_test == 6:
            motor_left.disable()
            motor_right.disable()
        elif button_test == 7:
            motor_left.set_effort(-25)
            motor_right.set_effort(25)
        elif button_test == 8:
            pass

        now = ticks_us()                          # present time [us] 
        if ticks_diff(deadline, now) <= 0:        # deadline elapsed 
            # Run looping code here; can reference "start" and "now" 
            # variables using ticks_diff() for timestamping actions 
            # of code (like data collection) 
            encoder_left.update()
            encoder_right.update()
            print(f"{encoder_left.position}, {encoder_right.position}")
            deadline = ticks_add(deadline, interval)# prep next deadline 
        
if __name__ == "__main__":
    main()


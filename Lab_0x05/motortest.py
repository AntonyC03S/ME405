from Motor_Driver import Motor
from pyb import Timer, Pin, I2C, delay  #type: ignore

tim3 = Timer(3, freq=20000)

motor_left   = Motor(Pin.cpu.C8, Pin.cpu.A10,  Pin.cpu.B2,  tim3, 3)  
motor_right  = Motor(Pin.cpu.C9, Pin.cpu.B12, Pin.cpu.B14, tim3, 4) 

motor_left.enable()
motor_right.enable()
motor_left.set_effort(50)
motor_right.set_effort(50)

stop_pin = Pin.cpu.C10   
stop_pin.init(Pin.IN, Pin.PULL_UP)

while True:
    state = stop_pin.value()

    if state == 1:
        motor_left.set_effort(0)
        motor_right.set_effort(0)
        break 

    delay(10) 
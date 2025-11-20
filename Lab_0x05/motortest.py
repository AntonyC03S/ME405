from Motor_Driver import Motor
from pyb import Timer, Pin, I2C, delay


tim3 = Timer(3, freq=20000)
motor_left = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)  
motor_right = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B14, tim3, 2) 
motor_left.enable()
motor_right.enable()
motor_left.set_effort(50)
motor_right.set_effort(50)
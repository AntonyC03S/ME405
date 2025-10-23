from Controller import Controller
from Motor_Driver import Motor
from Encoder_Driver import Encoder
from pyb import Pin, Timer
from time import sleep_ms

encoder_left  = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)
controller_left = Controller(2,2,0)
controller_right = Controller(2,2,0)
tim3 = Timer(3, freq=20000)
motor_left = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)  
motor_right  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, tim3, 2) 
motor_left.enable()
motor_right.enable()
motor_left.set_effort(10)
motor_right.set_effort(10)

while True:
    encoder_left.update()
    encoder_right.update()
    hi = controller_right.update(3, float(encoder_right.velocity) * -1)
    bye = controller_left.update(3, float(encoder_left.velocity))
    motor_left.set_effort(10+bye)
    motor_right.set_effort(10+hi)
    print(encoder_right.velocity,encoder_left.velocity, hi, bye)
    sleep_ms(100)



from Controller_Class import Controller
from Motor_Driver import Motor
from Encoder_Driver import Encoder
from pyb import Pin, Timer
from time import sleep_ms
Pin(Pin.cpu.C6,  mode=Pin.ALT, alt=3) 
Pin(Pin.cpu.C7, mode=Pin.ALT, alt=3)
encoder_left  = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
encoder_right = Encoder(Timer(8, prescaler = 0, period = 0xFFFF),Pin.cpu.C6,Pin.cpu.C7)
controller_left = Controller(2.7,20,0.1)
controller_right = Controller(2,19,0.1)
tim3 = Timer(3, freq=20000)
motor_left   = Motor(Pin.cpu.C8, Pin.cpu.A10,  Pin.cpu.B2,  tim3, 3)  
motor_right  = Motor(Pin.cpu.C9, Pin.cpu.B12, Pin.cpu.B14, tim3, 4) 
motor_left.enable()
motor_right.enable()
motor_left.set_effort(5)
motor_right.set_effort(5)

while True:
    encoder_left.update()
    encoder_right.update()
    right_gain = controller_right.update(10, float(encoder_right.velocity) * -1) 
    left_gain = controller_left.update(10, float(encoder_left.velocity))
    motor_left.set_effort(5+ left_gain)
    motor_right.set_effort(5+ right_gain)
    print(encoder_left.velocity, encoder_right.velocity, left_gain, right_gain)
    sleep_ms(100)



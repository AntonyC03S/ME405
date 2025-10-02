from pyb import Pin, Timer, ADC, ExtInt # type: ignore
from array import array


ON = False
def button_toggle(the_pin):
    global ON
    ON = not ON

button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_toggle)
Led = Pin(Pin.cpu.A5, mode=Pin.OUT_PP)
#Code does not work. Something to do with LED pwm thing and not activating something right
Motor_EN = Pin(Pin.cpu.B4, mode=Pin.OUT_PP, value=0)
Motor_Dir = Pin(Pin.cpu.B3, mode=Pin.OUT_PP, value=0)
Motor_Eff = Pin(Pin.cpu.A3, mode=Pin.OUT_PP, value=0)

while (True):
    if not ON:
        Motor_EN.low()
        Motor_Dir.low()
        Motor_Eff.low()
        Led.low()
        continue
    Motor_EN.high()
    Motor_Dir.high()
    Motor_Eff.high()
    Led.high()


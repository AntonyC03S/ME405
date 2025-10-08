from pyb import Pin, Timer, ADC, ExtInt # type: ignore
from time import ticks_us, ticks_diff   # Use to get dt value in update()

def main():
    ON = False
    def button_toggle(the_pin):
        global ON
        ON = not ON

    button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_toggle)
    #Led = Pin(Pin.cpu.A5, mode=Pin.OUT_PP)
    #Code does not work. Something to do with LED pwm thing and not activating something right
    Motor_EN = Pin(Pin.cpu.B4, mode=Pin.OUT_PP, value=0)
    Motor_Dir = Pin(Pin.cpu.B3, mode=Pin.OUT_PP, value=0)
    Motor_Eff = Pin(Pin.cpu.A3, mode=Pin.Pin.AF_PP)
    tim2 = Timer(2, freq=20000)
    t2ch1 = tim2.channel(1, pin=Pin.cpu.A5, mode=Timer.PWM, pulse_width_percent=50)

    while (True):
        if not ON:
            Motor_EN.low()
            Motor_Dir.low()
            #Motor_Eff.low()
            t2ch1.pulse_width_percent(0)
            continue
        Motor_EN.high()
        Motor_Dir.high()
        #Motor_Eff.high()
        t2ch1.pulse_width_percent(50)


if __name__ == "__main__":
    main()



# testing motor driver
#mot_left  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, Timer(3, freq=20000), 2)
#mot_left.enable()
#mot_left.set_effort(50)
tim = Timer(1)
ChA_chan = tim.channel(1, pin = Pin.cpu.A8, mode=Timer.ENC_AB)
sCHB_chan = tim.channel(2, pin = Pin.cpu.A9, mode=Timer.ENC_AB)

while True:
    print(tim.counter)
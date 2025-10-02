from pyb import Pin, Timer, ADC, ExtInt
from array import array


def tim_cb(tim):
    global data, idx, done
    data[idx] = adc.read()
    if idx == 100:
        PC1.high()
    idx += 1
    if idx >= 1000:
        tim7.callback(None)
        done = True

ON = False
def button_LED_toggle(the_pin):
    global ON
    ON = not ON

button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_LED_toggle)
PC0 = Pin(Pin.cpu.C0, mode=Pin.IN)
PC1 = Pin(Pin.cpu.C1, mode=Pin.OUT_PP, value=0)
tim7 = Timer(7, freq=600)
adc = ADC(PC0)  

while (True):
    if not ON:
        PC1.low()  
        continue
    data = array('H', 1000*[0])
    idx = 0
    done = False

    PC1.low()         
    tim7.callback(tim_cb)

    while not done:
        pass

    for i in range(idx):
        print(i, data[i])
    ON = not ON

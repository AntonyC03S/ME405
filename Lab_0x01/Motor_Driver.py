from pyb import Pin, Timer # type: ignore

class Motor:
    '''A motor driver interface encapsulated in a Python class. Works with
       motor drivers using separate PWM and direction inputs such as the DRV8838
       drivers present on the Romi chassis from Pololu.'''
    
    def __init__(self, PWM: Pin, DIR: Pin, nSLP: Pin, tim: Timer, chan: int):
        '''Initializes a Motor object'''
        self._nSLP_pin = Pin(nSLP, mode=Pin.OUT_PP, value=0)
        self._DIR_pin  = Pin(DIR, mode=Pin.OUT_PP, value=0)
        self._PWM_chan = tim.channel(chan, pin = PWM, mode=Timer.PWM, pulse_width_percent=0)

    @property
    def nSLP_pin(self):
        return f"{self._nSLP_pin}"
    
    @property
    def DIR_pin(self):
        return f"{self._DIR_pin}"
    
    @property
    def PWM_chan(self):
        return f"{self._PWM_chan}"
    
    def set_effort(self, effort: float):
        '''Sets the present effort requested from the motor based on an input value
           between -100 and 100'''
        if effort > 0:
            self._DIR_pin.low()
            self._PWM_chan.pulse_width_percent(effort)
        else:
            self._DIR_pin.high()
            self._PWM_chan.pulse_width_percent(-effort)
            
    def enable(self):
        '''Enables the motor driver by taking it out of sleep mode into brake mode'''
        self._nSLP_pin.high()
            
    def disable(self):
        '''Disables the motor driver by taking it into sleep mode'''
        self._nSLP_pin.low()

# testing motor driver
#mot_left  = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B11, Timer(3, freq=20000), 2)
#mot_left.enable()
#mot_left.set_effort(50)

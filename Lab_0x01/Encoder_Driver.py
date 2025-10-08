from pyb import Pin, Timer # type: ignore
from time import ticks_us, ticks_diff   # Use to get dt value in update()

class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, tim: Timer, chA_pin: Pin, chB_pin: Pin, chA_chan: int, chB_chan: int):
        '''Initializes an Encoder object'''

        self._ChA_chan = tim.channel(chA_chan, pin = chA_pin, mode=Timer.PWM, pulse_width_percent=0)
        self._CHB_chan = tim.channel(chB_chan, pin = chB_pin, mode=Timer.PWM, pulse_width_percent=0)
        self._position   = 0   # Total accumulated position of the encoder
        self._prev_count = 0      # Counter value from the most recent update
        self._delta      = 0      # Change in count between last two updates
        self._dt         = 0      # Amount of time between last two updates
        self._AR         = 65,535 # 16-bit timers maximal count value
    
    def update(self):
        '''Runs one update step on the encoder's timer counter to keep
           track of the change in count and check for counter reload'''
        
        if self._position is None:
            self._position == ticks_us()
            return
        
        now = ticks_us()
        self._delta = ticks_diff(self._position , now)
        # Overflow: delta < -(AR+1)/2; to correct, delta += AR + 1 
        if self._delta < -(self._AR+1)/2:
            self._delta += self._AR +1

        # Underflow: delta > (AR+1)/2; to correct, delta -= AR + 1 
        elif self._delta > (self._AR+1)/2:
            self._delta -= self._AR +1
            

    @property
    def position(self):
        '''Returns the most recently updated value of position as determined
           within the update() method'''
        return f"{self._position}"
    
    @property   
    def velocity(self):
        '''Returns a measure of velocity using the the most recently updated
           value of delta as determined within the update() method'''
        return f"{self._delta/self._dt}"
    
    def zero(self):
        '''Sets the present encoder position to zero and causes future updates
           to measure with respect to the new zero position'''
        self._position = 0

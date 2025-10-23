from time import ticks_us, ticks_diff

class Controller:
    
    def __init__(self, KP: float, KI: float, KD: float):

        self._KP = KP
        self._KI = KI
        self._KD = KD

        self._prev_time = ticks_us()
        self._prev_error = 0
        self._integral = 0
        self._gain = 0
        self._output = 0

    def update(self, setpoint: float, measured: float):

        now = ticks_us()
        dt = ticks_diff(now, self._prev_time) / 1_000_000

        error = setpoint - measured

        Pgain = error * self._KP
        self._integral += error * dt
        Igain = self._integral * self._KI
        Dgain = ((error - self._prev_error) / dt) * self._KD

        self._gain = Pgain + Igain + Dgain

        if self._gain >= 100:
            self._output = 100
        elif self._gain <= 0:
            self._output = 0
        else:
            self._output = self._gain
            
        self._prev_error = error
        self._prev_time = now

        return self._output






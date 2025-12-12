"""! @file Controller_Class.py
@brief The Controller Class is used to implment a PID feedback loop

The Controller Class implments the PID contoller which are Proportional,
Intergral and Derivative.
"""
from time import ticks_us, ticks_diff

class Controller:
    """! PID feedback controller.

    @brief Implements a real-time PID controller with anti windup and
    output saturation.

    The controller outputs a effort limited to the range `[-100, 100]`.

    Features:
    - Proportional, integral, and derivative 
    - Anti-windup integral behavior
    - Automatic output saturation
    """

    def __init__(self, KP: float, KI: float, KD: float):
        """! Initialize a PID controller.

        @param KP Proportional gain.
        @param KI Integral gain.
        @param KD Derivative gain.
        """
        self._KP = KP
        self._KI = KI
        self._KD = KD

        self._prev_time = ticks_us()
        self._prev_error = 0.0
        self._integral = 0.0
        self._gain = 0.0       
        self._output = 0.0     

    def update(self, setpoint: float, measured: float) -> float:
        """! Compute the PID output for the current measurement.

        @brief Performs one update step of the PID controller.

        @param setpoint  Desired value.
        @param measured  Actual measured value.
        @return Effort output in the range [-100, 100].
        """
        now = ticks_us()
        dt = ticks_diff(now, self._prev_time) / 1_000_000  # convert µs → seconds
        
        error = setpoint - measured

        # Integral term (with anti-windup)
        if self._output == self._gain:
            self._integral += error * dt
        else:
            self._integral = 0

        # PID terms
        P_gain = error * self._KP
        I_gain = self._integral * self._KI
        D_gain = ((error - self._prev_error) / dt) * self._KD
        self._gain = P_gain + I_gain + D_gain


        # Output saturation
        if self._gain >= 100:
            self._output = 100
        elif self._gain <= -100:
            self._output = -100
        else:
            self._output = self._gain


        self._prev_error = error
        self._prev_time = now

        return self._output

"""! @file controller.py
@brief PID controller implementation for robot motion control.

This module defines the :class:`Controller` class which implements a
standard PID (Proportional–Integral–Derivative) feedback controller.
It is compatible with MicroPython through the use of `ticks_us()` for
timekeeping.
"""

from time import ticks_us, ticks_diff
import math  # noqa: F401


class Controller:
    """! PID feedback controller.

    @brief Implements a real-time PID controller with anti-windup and
    output saturation.

    The controller outputs a value limited to the range `[-100, 100]`,
    making it suitable for motor effort commands in your robot.

    Features:
    - Proportional, integral, and derivative terms
    - Derivative on measurement error
    - Anti-windup integral behavior
    - Automatic output saturation
    """

    def __init__(self, KP: float, KI: float, KD: float):
        """! Initialize a PID controller.

        @param KP Proportional gain.
        @param KI Integral gain.
        @param KD Derivative gain.

        The controller stores internal timestamps and error history
        for computing numerical derivatives and integrals.
        """
        self._KP = KP
        self._KI = KI
        self._KD = KD

        self._prev_time = ticks_us()
        self._prev_error = 0.0
        self._integral = 0.0
        self._gain = 0.0       # Raw PID output before saturation
        self._output = 0.0     # Saturated output [-100, 100]

    def update(self, setpoint: float, measured: float) -> float:
        """! Compute the PID output for the current measurement.

        @brief Performs one update step of the PID controller.

        @param setpoint  Desired value.
        @param measured  Actual measured value.
        @return Control output in the range [-100, 100].

        This method:
        - Computes error
        - Calculates P, I, and D components
        - Runs anti-windup on the integral term
        - Applies output saturation
        - Returns the bounded control signal
        """
        now = ticks_us()
        dt = ticks_diff(now, self._prev_time) / 1_000_000  # convert µs → seconds

        # Protect against dt = 0 (should rarely happen)
        if dt <= 0:
            dt = 1e-6

        # Error signal
        error = setpoint - measured

        # Proportional term
        P_gain = error * self._KP

        # Integral term (with anti-windup)
        if self._output == self._gain:
            self._integral += error * dt
        else:
            self._integral = 0

        I_gain = self._integral * self._KI

        # Derivative term
        D_gain = ((error - self._prev_error) / dt) * self._KD

        # Combine
        self._gain = P_gain + I_gain + D_gain

        # Output saturation
        if self._gain >= 100:
            self._output = 100
        elif self._gain <= -100:
            self._output = -100
        else:
            self._output = self._gain

        # Save state
        self._prev_error = error
        self._prev_time = now

        return self._output

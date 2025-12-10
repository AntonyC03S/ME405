"""! @file Motor_Driver.py
@brief Motor driver class for PWM + direction motor controllers.

This module defines the :class:`Motor` class, used for controlling DC motors
with a PWM pin, direction pin, and nSLP (sleep) pin.

"""

from pyb import Pin, Timer  # type: ignore


class Motor:
    """! Motor driver interface using PWM + direction control.

    @brief Controls a brushed DC motor using a PWM pin, a direction pin,
    and an nSLP pin.

    The driver accepts effort values from `-100` to `100`, where:

    - Positive → forward (DIR low)
    - Negative → reverse (DIR high)
    - Zero     → motor brake (0% PWM)

    """

    def __init__(self, PWM: Pin, DIR: Pin, nSLP: Pin, tim: Timer, chan: int):
        """! Initialize a Motor object.

        @param PWM   Pin object (or pin name) connected to PWM input.
        @param DIR   Pin object (or pin name) connected to direction input.
        @param nSLP  Pin used to enable/disable the motor driver.
        @param tim   Timer configured to generate PWM.
        @param chan  Timer channel number for the PWM output.

        This constructor sets all pins to output mode and initializes
        the PWM channel with 0% duty cycle.
        """
        self._nSLP_pin = Pin(nSLP, mode=Pin.OUT_PP, value=0)
        self._DIR_pin = Pin(DIR, mode=Pin.OUT_PP, value=0)
        self._PWM_chan = tim.channel(
            chan, pin=PWM, mode=Timer.PWM, pulse_width_percent=0
        )

    @property
    def nSLP_pin(self):
        """! Get the nSLP pin object."""
        return self._nSLP_pin

    @property
    def DIR_pin(self):
        """! Get the direction pin object."""
        return self._DIR_pin

    @property
    def PWM_chan(self):
        """! Get the PWM channel object."""
        return self._PWM_chan

    def set_effort(self, effort: float):
        """! Set motor effort level between -100 and 100.

        @brief Controls the PWM duty cycle and direction pin based on effort.

        @param effort Desired effort from -100 (reverse max) to +100 (forward max).

        Behavior:
        - If effort > 0 → forward direction
        - If effort < 0 → reverse direction
        - If effort = 0 → motor output = brake (0% PWM)

        Effort values are automatically clamped to [-100, 100].
        """

        # Special case: stop motor
        if effort == 0:
            self._PWM_chan.pulse_width_percent(0)
            return

        # Clamp effort
        if effort > 100:
            effort = 100
        if effort < -100:
            effort = -100

        # Forward direction
        if effort > 0:
            self._DIR_pin.low()
            self._PWM_chan.pulse_width_percent(effort)

        # Reverse direction
        else:
            self._DIR_pin.high()
            self._PWM_chan.pulse_width_percent(-effort)

    def enable(self):
        """! Enable the motor driver.

        @brief Takes the DRV8838 out of sleep mode and sets PWM to 0%.

        This places the driver in **brake mode** until an effort is applied.
        """
        self._nSLP_pin.high()
        self._PWM_chan.pulse_width_percent(0)

    def disable(self):
        """! Disable the motor driver.

        @brief Sets PWM to 0% and puts the H-bridge into sleep mode.

        Useful for saving power or ensuring the motor will not move.
        """
        self._PWM_chan.pulse_width_percent(0)
        self._nSLP_pin.low()

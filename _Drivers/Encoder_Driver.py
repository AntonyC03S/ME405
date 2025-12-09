"""! @file Encoder_Driver.py
@brief Quadrature encoder driver for a MicroPython Pyboard.

This module gives the :class:`Encoder` class that wraps a hardware
timer configured in encoder mode and returns position and
velocity in useful units (radians, meters, and mm/s).
"""

from pyb import Pin, Timer  # type: ignore
from time import ticks_us, ticks_diff  # Use to get dt value in update()
import math


class Encoder:
    """! Quadrature encoder interface.

    @brief Decodes a quadrature encoder using a hardware timer in ENC_AB mode.

    The encoder uses a 16-bit timer configured in encoder mode and keeps
    track of:

    - Total position (in ticks)
    - Time between updates
    - Velocity 

    """

    def __init__(
        self,
        tim: Timer,
        chA_pin: Pin,
        chB_pin: Pin,
        chA_chan: int = 1,
        chB_chan: int = 2,
    ):
        """! Initialize an Encoder instance.

        @param tim      Timer instance configured for encoder mode.
        @param chA_pin  Pin object connected to encoder channel A.
        @param chB_pin  Pin object connected to encoder channel B.
        @param chA_chan Timer channel number used for channel A (default: 1).
        @param chB_chan Timer channel number used for channel B (default: 2).

        The timer is configured in @c Timer.ENC_AB mode on the two channels.
        Internal state variables keep track of position, delta counts, and
        timestamps between updates.
        """
        self._tim = tim
        self._ChA_chan = tim.channel(chA_chan, pin=chA_pin, mode=Timer.ENC_AB)
        self._CHB_chan = tim.channel(chB_chan, pin=chB_pin, mode=Timer.ENC_AB)

        #: Total accumulated encoder position in timer counts (ticks).
        self._position = 0

        #: Previous raw timer count value from the last update.
        self._prev_count = 0

        #: Timestamp of the previous update in microseconds.
        self._prev_time = 0

        #: Change in counts between the last two updates.
        self._delta = 0

        #: Time between the last two updates in microseconds.
        self._dt = 0

        #: 16-bit timer auto-reload (maximum count value).
        self._AR = 65535  # 16-bit timers maximal count value

    def update(self):
        """! Update the encoder state.

        @brief Reads the timer counter, handles overflow/underflow and
        updates position, delta, and time step.

        This method must be called periodically in the main loop to keep
        @ref position and @ref velocity up-to-date.
        """
        # Read current timer count
        now_count = self._tim.counter()

        # Compute delta in counts, accounting for wraparound
        self._delta = ticks_diff(self._prev_count, now_count)
        self._prev_count = now_count

        # Overflow: delta < -(AR+1)/2; correct by adding AR + 1
        if self._delta < -(self._AR + 1) / 2:
            self._delta += self._AR + 1

        # Underflow: delta > (AR+1)/2; correct by subtracting AR + 1
        elif self._delta > (self._AR + 1) / 2:
            self._delta -= self._AR + 1

        # Integrate position
        self._position += self._delta

        # Update timing
        now = ticks_us()
        self._dt = ticks_diff(now, self._prev_time)
        self._prev_time = now

    @property
    def position(self) -> float:
        """! Get angular position of the encoder in radians.

        @return Current angular position in radians.

        The raw encoder count is converted using a fixed
        @c ticks_per_rev = 1437.1.
        """
        return self._position * (2 * math.pi / 1437.1)

    def distance_traveled(self, radius: float = 35.0, ticks_per_rev: float = 1437.1) -> float:
        """! Get absolute wheel distance traveled.

        @brief Computes the total linear distance the wheel has traveled.

        @param radius       Wheel radius in millimeters (default: 35 mm).
        @param ticks_per_rev Encoder ticks per mechanical revolution
                             (default: 1437.1).
        @return Distance traveled in meters.

        The distance is computed as:

        @f[
        d = 2 \pi r \cdot \frac{N}{\text{ticks\_per\_rev}}
        @f]

        where @f$ N @f$ is the accumulated encoder count.
        """
        rev = self._position / float(ticks_per_rev)
        dist_m = 2 * math.pi * (radius / 1000.0) * rev
        return dist_m

    def define_distance_traveled(self, traveled: float, radius: float = 35.0) -> None:
        """! Force the internal position to match a desired travel distance.

        @param traveled Target distance in millimeters.
        @param radius   Wheel radius in millimeters (default: 35 mm).

        This can be used to "zero" or re-reference the encoder based on a
        known physical position.
        """
        self._position = traveled / radius

    @property
    def velocity(self) -> float:
        """! Get angular velocity in radians per second.

        @return Angular velocity in rad/s based on the last update interval.

        Velocity is computed from the count delta and time delta:

        @f[
        \omega = \frac{\Delta N}{\Delta t}\cdot
                 \frac{2 \pi}{\text{ticks\_per\_rev}}
        @f]

        where @f$ \Delta t @f$ is in seconds.
        """
        if self._dt == 0:
            return 0.0
        return (self._delta / self._dt) * (2 * math.pi * 1_000_000 / 1437.1)

    def linear_velocity(self, radius: float = 35.0) -> float:
        """! Get linear wheel velocity in mm/s.

        @param radius Wheel radius in millimeters (default: 35 mm).
        @return Linear velocity at the wheel rim in mm/s.
        """
        if self._dt == 0:
            return 0.0
        # angular velocity [rad/s] * radius [mm]
        return (self._delta / self._dt) * (2 * math.pi * 1_000_000 / 1437.1) * radius

    def zero(self) -> None:
        """! Zero the position counter.

        @brief Sets the present encoder position to zero so that future
        updates measure relative motion from this point.
        """
        self._position = 0


"""! @file discretized_estimation.py
@brief Discrete-time state observer for the Romi robot.

This module implements a Luenberger-style state observer for the Romi robot
using discrete-time system matrices and `ulab` for lightweight linear algebra
in MicroPython.

The observer estimates the state vector

@f[
x = \\begin{bmatrix}
\\omega_L \\\\
\\omega_R \\\\
s \\\\
\\psi
\\end{bmatrix}
@f]

where:

- @f$ \\omega_L, \\omega_R @f$ are left/right wheel angular speeds
- @f$ s @f$ is (approximately) the forward arc length / position
- @f$ \\psi @f$ is the heading (yaw angle, in radians)
"""

from ulab import numpy as np
from math import pi


class RomiObserver:
    """! Discrete-time Romi state observer.

    @brief Estimates robot states from motor commands and sensor feedback.

    The observer uses a discrete-time linear model:

    @f[
    x_{k+1} = A_d x_k + B_d u_k + L (y_k - C x_k)
    @f]

    with measurements:

    - @f$ S_L, S_R @f$: left/right encoder arc lengths [m]
    - @f$ \\psi @f$: IMU heading [rad]
    - @f$ \\dot{\\psi} @f$: IMU yaw rate [rad/s]

    and state:

    - @f$ x = [\\omega_L, \\omega_R, s, \\psi]^T @f$
    """

    def __init__(self, Ad, Bd, r: float = 0.035, l: float = 0.141, L=None):
        """! Initialize the Romi observer.

        @param Ad Discrete-time A matrix (currently unused; internal default is used).
        @param Bd Discrete-time B matrix (currently unused; internal default is used).
        @param r  Wheel radius [m] (default: 0.035).
        @param l  Wheel track width [m] (default: 0.141).
        @param L  Observer gain matrix (4x4). If None, a default gain is used.

        @note Currently, the constructor uses built-in Ad and Bd matrices tuned
        for a specific sampling period and robot model. The @p Ad and @p Bd
        parameters are present for future flexibility but are not applied.
        """
        # Discrete-time system matrices (pre-computed offline)
        self.Ad = np.array(
            [
                [0.904837, 0, 0, 0],
                [0, 0.904837, 0, 0],
                [0.000167, 0.000167, 1, 0],
                [-0.002362, 0.002362, 0, 1],
            ]
        )
        self.Bd = np.array(
            [
                [0.553633, 0],
                [0, 0.553633],
                [0.000049, 0.000049],
                [-0.000699, 0.000699],
            ]
        )

        # Output matrix maps state -> measured outputs [SL, SR, psi, psidot]
        self.C = np.array(
            [
                [0, 0, 1, -l / 2],   # SL
                [0, 0, 1,  l / 2],   # SR
                [0, 0, 0, 1],        # psi
                [-r / l, r / l, 0, 0]  # psidot
            ]
        )

        if L is None:
            # Starter gain (tune on-robot: larger -> faster correction, but noisier)
            self.L = np.array(
                [
                    [0.08, -0.08, 0.00, -0.02],
                    [-0.08, 0.08, 0.00, 0.02],
                    [0.35, 0.35, 0.00, 0.00],
                    [0.00, 0.00, 0.50, 0.70],
                ]
            )
        else:
            self.L = np.array(L)

        # State vector x = [wL, wR, s, psi]^T
        self.x = np.zeros((4, 1))

    def reset(self, x0=None) -> None:
        """! Reset the observer state.

        @param x0 Optional initial state vector (4x1). If None, zeros are used.

        This is useful when re-starting an experiment or re-initializing
        the estimate after a large disturbance.
        """
        self.x = np.array(x0) if x0 is not None else np.zeros((4, 1))

    def step(self, u, SL, SR, psi_deg: float, yawrate_dps: float):
        """! Advance the observer one time step.

        @brief Updates the state estimate based on input and sensor readings.

        @param u           Control input vector (2x1) with motor voltages [[uL], [uR]].
        @param SL          Left wheel arc length [m] from encoder.
        @param SR          Right wheel arc length [m] from encoder.
        @param psi_deg     IMU heading [deg].
        @param yawrate_dps IMU yaw rate [deg/s].
        @return Updated state estimate @f$ x_{k+1} @f$ as a (4x1) array.

        The method:
        - Converts IMU angles from degrees to radians
        - Forms measurement vector y = [SL, SR, psi, psidot]^T
        - Computes output estimate yhat = C x
        - Applies observer correction using the gain L
        """
        # Convert IMU readings to radians / radians per second
        psi = psi_deg * (pi / 180.0)
        psidot = yawrate_dps * (pi / 180.0)

        # Measurement vector
        y = np.array([[SL], [SR], [psi], [psidot]])

        x = self.x
        yhat = np.dot(self.C, x)
        e = y - yhat

        # Observer update: x_{k+1} = A_d x_k + B_d u_k + L (y - C x_k)
        x_next = np.dot(self.Ad, x) + np.dot(self.Bd, u) + np.dot(self.L, e)
        self.x = x_next
        return x_next

    def state(self):
        """! Get the current state estimate.

        @return State vector x as (4x1) array:
                [wL, wR, s, psi]^T.
        """
        return self.x

    def outputs_hat(self):
        """! Get estimated outputs based on current state.

        @brief Computes @f$ \\hat{y} = C x @f$.

        @return Estimated output vector (4x1):
                [SL_hat, SR_hat, psi_hat, psidot_hat]^T.
        """
        return np.dot(self.C, self.x)


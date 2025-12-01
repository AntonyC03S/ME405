# romi_observer.py  (MicroPython + ulab)
from ulab import numpy as np
from math import pi

class RomiObserver:
    def __init__(self, Ad, Bd, r = 0.035, l = 0.141, L=None):
        self.Ad = np.array([[0.904837, 0, 0, 0], [0, 0.904837, 0, 0], [0.000167, 0.000167, 1, 0], [-0.002362, 0.002362, 0, 1]])
        self.Bd = np.array([[0.553633, 0], [0, 0.553633], [0.000049, 0.000049], [-0.000699,  0.000699]])
        self.C  = np.array([[0, 0, 1, -l/2],
                            [0, 0, 1,  l/2],
                            [0, 0, 0, 1],
                            [-r/l, r/l, 0, 0]])
        if L is None:
            # Starter gain (tune on-robot):
            # bigger -> faster correction (but noisier). Start modest.
            self.L = np.array([
    [ 0.08, -0.08, 0.00, -0.02], 
    [-0.08,  0.08, 0.00,  0.02], 
    [ 0.35,  0.35, 0.00,  0.00],  
    [ 0.00,  0.00, 0.50,  0.70],  
])
        else:
            self.L = np.array(L)

        self.x = np.zeros((4,1))  # [wL, wR, s, psi]^T

    def reset(self, x0=None):
        self.x = np.array(x0) if x0 is not None else np.zeros((4,1))

    def step(self, u, SL, SR, psi_deg, yawrate_dps):
        """
        u: (2,1) np.array volts [[uL],[uR]]
        SL, SR: encoder arc lengths [m]
        psi_deg: IMU heading [deg]
        yawrate_dps: IMU yaw rate [deg/s]

        returns xhat (4,1)
        """
        # Build y (convert IMU to rad, rad/s)
        psi    = psi_deg * (pi/180.0)
        psidot = yawrate_dps * (pi/180.0)
        y = np.array([[SL],[SR],[psi],[psidot]])

        x = self.x
        yhat = np.dot(self.C, x)
        e = y - yhat
        x_next = np.dot(self.Ad, x) + np.dot(self.Bd, u) + np.dot(self.L, e)
        self.x = x_next
        return x_next

    # Convenience accessors
    def state(self):
        return self.x

    def outputs_hat(self):
        return np.dot(self.C, self.x)

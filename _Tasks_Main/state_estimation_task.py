from pyb import Pin, Timer # type: ignore
from discretized_estimation import RomiObserver
from imu_Driver import IMU
from pyb import Timer, Pin, I2C, delay
import time
from ulab import numpy as np
from math import pi, sin, cos

def state_task(shares):
    state = 0
    (L_volt, R_volt, lpos, rpos, s, a) = shares

    # States
    Init = 0
    Stop = 1
    Run = 2
    x = 0
    y = 0
    r      = 0.035  
    l      = 0.141   
    Ts_ms  = 10    
    s_mm   = 0.0     
    a_deg  = 0.0  

    last_update_ms = time.ticks_ms()
    psi0_set = False
    psi0_deg = 0.0

    # Placeholders so Python knows these exist in this scope
    imu = None
    obs = None

    Ad = [
    [ 0.904837,  0.      ,  0.      ,  0.      ],
    [ 0.      ,  0.904837,  0.      ,  0.      ],
    [ 0.000167,  0.000167,  1.      ,  0.      ],
    [-0.002362,  0.002362,  0.      ,  1.      ],
    ]
    Bd = [
        [ 0.553633,  0.      ],
        [ 0.      ,  0.553633],
        [ 0.000049,  0.000049],
        [-0.000699,  0.000699],
    ]
    L = [
    [ -67.8571, -67.8571, 0.00, -1.0071], 
    [-67.8571,  -67.8571, 0.00,  1.0071], 
    [ 0.5,  0.5, 0.00,  0.00],
    [ -0.0349,  0.0349,  0.4951,  1],
]
    def clamp(v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    def wrap_deg180(a):
        while a <= -180:
            a += 360
        while a > 180:
            a -= 360
        return a


    while True:
        if state == Init:
            i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)
            imu = IMU(i2c, addr=0x28)
            delay(700)
            imu.push_cal_data()
            delay(100)
            imu._set_mode("NDOF")
            delay(100)
            obs = RomiObserver(Ad, Bd, r, l, L=L)
            state = Run

        elif state == Stop:
            pass

        elif state == Run:
            now = time.ticks_ms()
            dt_ms = time.ticks_diff(now, last_update_ms)
            if dt_ms < Ts_ms:
                yield state
                continue
            last_update_ms = now
            uL = float(L_volt.get())
            uR = float(R_volt.get())
            SL = float(lpos.get())
            SR = float(rpos.get())
            psi_abs = imu.read_heading()
            yaw_dps  = imu.read_yaw_rate()
            if not psi0_set:
                psi0_deg = psi_abs
                psi0_set = True
            psi_rel_deg = wrap_deg180(psi_abs - psi0_deg)
            u = np.array([[uL], [uR]])

            xhat = obs.step(u, SL, SR, psi_rel_deg, yaw_dps)

            s_mm  = float(xhat[2, 0]) * 1000.0
            a_deg = float(xhat[3, 0]) * (180.0 / pi)


            s.put(s_mm)
            a.put(a_deg)
            print(s_mm,a_deg)
        yield state


if __name__ == "__main__":
     pass
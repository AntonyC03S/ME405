from ulab import numpy as np
from pyb import Timer, Pin, I2C, delay
from math import pi
from discretized_estimation import RomiObserver
from imu_Driver import IMU
from Encoder_Driver import Encoder
from Motor_Driver import Motor
import time

# --- your robot params ---
r   = 0.035   # wheel radius [m]  <-- set yours
l = 0.141   # wheelbase [m]     <-- set yours

# --- your matrices (paste exactly as printed) ---
Ad = [[ 0.904837,  0.      ,  0.      ,  0.      ],
      [ 0.      ,  0.904837,  0.      ,  0.      ],
      [ 0.000167,  0.000167,  1.      ,  0.      ],
      [-0.002362,  0.002362,  0.      ,  1.      ]]

Bd = [[ 0.553633,  0.      ],
      [ 0.      ,  0.553633],
      [ 0.000049,  0.000049],
      [-0.000699,  0.000699]]

L = [[ 0.08, -0.08, 0.00, -0.02],  # wL: use yaw-rate innovation a bit to correct diff
    [-0.08,  0.08, 0.00,  0.02],  # wR: opposite sign
    [ 0.35,  0.35, 0.00,  0.00],  # s : CORRECT -> average of (SL, SR)
    [ 0.00,  0.00, 0.50,  0.70]]


obs = RomiObserver(Ad, Bd, r, l, L=L)  
tim3 = Timer(3, freq=20000)
motor_left = Motor(Pin.cpu.A6, Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)  
motor_right = Motor(Pin.cpu.A7, Pin.cpu.B12, Pin.cpu.B14, tim3, 2) 
motor_left.enable()
motor_right.enable()
encoder_left  = Encoder(Timer(1, prescaler = 0, period = 0xFFFF),Pin.cpu.A8,Pin.cpu.A9)
encoder_right = Encoder(Timer(2, prescaler = 0, period = 0xFFFF),Pin.cpu.A0,Pin.cpu.A1)
i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)
imu = IMU(i2c, addr=0x28)   
imu.push_cal_data()
time.sleep_ms(100)
imu._set_mode("NDOF")  # set to IMU mode
time.sleep_ms(100)

motor_left.set_effort(25)
motor_right.set_effort(25)
encoder_left.zero()
encoder_right.zero()

psi0_deg = imu.read_heading()   # reference heading (degrees)

def wrap_deg180(a):
    # wrap to (-180, 180]
    while a <= -180: a += 360
    while a >   180: a -= 360
    return a


v = 7.2 * .1


def loop_step():
    # 1) inputs (Volts)
    uL = v
    uR = v
    u = np.array([[uL],[uR]])

    # 2) measurements
    # If your Encoder exposes *methods*:
    # SL = encoder_left.distance_traveled()   # meters since last reset or absolute
    # SR = encoder_right.distance_traveled()  # meters
    # If it exposes *properties*, keep your original (but parentheses removed):
    encoder_left.update()
    encoder_right.update() 
    SL = encoder_left.distance_traveled()
    SR = encoder_right.distance_traveled()

    psi_deg = wrap_deg180(imu.read_heading() - psi0_deg)
    yaw_dps   = imu.read_yaw_rate()   # deg/s

    # 3) observer update
    xhat = obs.step(u, SL, SR, psi_deg, yaw_dps)

    # 4) use/publish the estimate
    # xhat = [wL, wR, s, psi]^T  (psi in rad)
    # Replace with your Share/Queue publish call:
    print("xhat:", [float(xhat[0,0]), float(xhat[1,0]), float(xhat[2,0]), float(xhat[3,0])])


# --- Simple periodic loop (blocking) ---
while True:
    loop_step()
    delay(int(0.01*1000))   # ~10 ms

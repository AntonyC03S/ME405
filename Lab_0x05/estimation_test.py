from ulab import numpy as np
from pyb import Timer, Pin, I2C, delay
from math import pi
import time
from discretized_estimation import RomiObserver
from imu_Driver import IMU
from Encoder_Driver import Encoder
from Motor_Driver import Motor
from Controller_Class import Controller   


r      = 0.035  
l      = 0.141   
Ts_ms  = 10    


s_mm   = 0.0     
a_deg  = 0.0     


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
    [ 0.08, -0.08, 0.00, -0.02], 
    [-0.08,  0.08, 0.00,  0.02], 
    [ 0.35,  0.35, 0.00,  0.00],  
    [ 0.00,  0.00, 0.50,  0.70],  
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

tim3 = Timer(3, freq=20000)
motor_left  = Motor(Pin.cpu.A6,  Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)
motor_right = Motor(Pin.cpu.A7,  Pin.cpu.B12, Pin.cpu.B14, tim3, 2)
motor_left.enable()
motor_right.enable()

encoder_left  = Encoder(Timer(1, prescaler=0, period=0xFFFF), Pin.cpu.A8, Pin.cpu.A9)
encoder_right = Encoder(Timer(2, prescaler=0, period=0xFFFF), Pin.cpu.A0, Pin.cpu.A1)

controller_left  = Controller(2.5, 20.0, 0.1)
controller_right = Controller(2.5, 20.0, 0.1)

i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)
imu = IMU(i2c, addr=0x28)
delay(700)
imu.push_cal_data()
delay(100)
imu._set_mode("NDOF")
delay(100)

obs = RomiObserver(Ad, Bd, r, l, L=L)

psi0_deg = imu.read_heading()

def get_rel_deg():
    global psi0_deg
    psi_abs = imu.read_heading()
    return wrap_deg180(psi_abs - psi0_deg)

def reset():
    global s_mm, a_deg, psi0_deg
    encoder_left.zero()
    encoder_right.zero()
    encoder_left.update()
    encoder_right.update()
    obs.reset()
    psi0_deg = imu.read_heading()
    s_mm  = 0.0
    a_deg = 0.0

def step(effL, effR):
    global s_mm, a_deg
    effL = clamp(effL, -100, 100)
    effR = clamp(effR, -100, 100)
    motor_left.set_effort(effL)
    motor_right.set_effort(effR)
    Vbatt = 7.2 
    uL = Vbatt * (effL / 100.0)
    uR = Vbatt * (effR / 100.0)
    u = np.array([[uL], [uR]])
    encoder_left.update()
    encoder_right.update()
    SL = float(encoder_left.distance_traveled())  
    SR = float(encoder_right.distance_traveled())
    psi_rel_deg = get_rel_deg()
    yaw_dps = imu.read_yaw_rate() 
    xhat = obs.step(u, SL, SR, psi_rel_deg, yaw_dps)
    s_mm  = float(xhat[2, 0]) * 1000.0
    a_deg = float(xhat[3, 0]) * (180.0 / pi)
    print("xhat:", float(xhat[0,0]), float(xhat[1,0]), s_mm, a_deg)
    delay(Ts_ms)

def step_straight():
    v_target = 10.0  
    Lgain = controller_left.update(v_target,  float(encoder_left.velocity))
    Rgain = controller_right.update(v_target, float(encoder_right.velocity))
    base_eff = 5.0
    effL = base_eff + Lgain
    effR = base_eff + Rgain
    step(effL, effR)

def straight(distance_mm, timeout_ms):
    global s_mm
    start_s = s_mm
    target  = distance_mm
    margin  = 5.0  
    while True:
        step_straight()
        traveled = s_mm - start_s
        if traveled >= (target - margin):
            break
    motor_left.set_effort(0)
    motor_right.set_effort(0)

def step_turn_cw(eff):
    v_target = 10.0
    Lgain = controller_left.update(v_target,  float(encoder_left.velocity))
    Rgain = controller_right.update(v_target, float(encoder_right.velocity))
    eff = clamp(eff, 0, 100)
    effL =  eff + Lgain  
    effR = -(eff + Rgain) 
    step(effL, effR)

def step_turn_ccw(eff):
    v_target = 10.0
    Lgain = controller_left.update(v_target,  float(encoder_left.velocity))
    Rgain = controller_right.update(v_target, float(encoder_right.velocity))
    eff = clamp(eff, 0, 100)
    effL = -(eff + Lgain)  
    effR =  (eff + Rgain)  
    step(effL, effR)

def delta_cw(psi_start, psi_now):
    d = psi_now - psi_start
    while d < 0:
        d += 360
    while d >= 360:
        d -= 360
    return d

def delta_ccw(psi_start, psi_now):
    d = psi_start - psi_now
    while d < 0:
        d += 360
    while d >= 360:
        d -= 360
    return d

def turn_cw(deg):
    KP_ANG = 1.0
    KI_ANG = 0.0
    KD_ANG = 0.05
    ctrl = Controller(KP_ANG, KI_ANG, KD_ANG)
    deg = abs(deg)
    psi_start = imu.read_heading()   
    eff_min  = 3.0
    eff_max  = 20.0
    while True:
        psi_now  = imu.read_heading()
        yaw_mag  = delta_cw(psi_start, psi_now)
        err      = deg - yaw_mag
        eff_cmd = ctrl.update(deg, yaw_mag)
        if eff_cmd <= 0:
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            delay(Ts_ms)
        else:
            local_eff_max = eff_min + 0.8 * err  
            if local_eff_max > eff_max:
                local_eff_max = eff_max
            if local_eff_max < eff_min:
                local_eff_max = eff_min
            eff = clamp(eff_cmd, eff_min, local_eff_max)
            step_turn_cw(eff)

def turn_ccw(deg):
    KP_ANG = 1.0
    KI_ANG = 0.0
    KD_ANG = 0.05
    ctrl = Controller(KP_ANG, KI_ANG, KD_ANG)
    deg = abs(deg)
    psi_start = imu.read_heading()  
    eff_min  = 3.0
    eff_max  = 20.0
    while True:
        psi_now  = imu.read_heading()
        yaw_mag  = delta_ccw(psi_start, psi_now)  
        err      = deg - yaw_mag
        eff_cmd = ctrl.update(deg, yaw_mag)
        if eff_cmd <= 0:
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            delay(Ts_ms)
        else:
            local_eff_max = eff_min + 0.8 * err
            if local_eff_max > eff_max:
                local_eff_max = eff_max
            if local_eff_max < eff_min:
                local_eff_max = eff_min
            eff = clamp(eff_cmd, eff_min, local_eff_max)
            step_turn_ccw(eff)

reset()
print("START SQUARE PATTERN")
print("Phase 1: straight 300 mm")
straight(300.0, timeout_ms=8000)
print("Phase 2: turn 90 CW (IMU)")
turn_cw(90.0, timeout_ms=6000)
print("Phase 3: straight 300 mm")
straight(300.0, timeout_ms=8000)
print("Phase 4: turn 180 CCW (IMU)")
turn_ccw(180.0, timeout_ms=9000)
print("Phase 5: straight 300 mm")
straight(300.0, timeout_ms=8000)
print("Phase 6: turn 90 CCW (IMU)")
turn_ccw(90.0, timeout_ms=6000)
print("Phase 7: straight 300 mm")
straight(300.0, timeout_ms=8000)
print("Phase 8: turn 180 CW (IMU)")
turn_cw(180.0, timeout_ms=9000)
motor_left.set_effort(0)
motor_right.set_effort(0)
print("Finished square pattern")

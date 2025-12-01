from ulab import numpy as np
from pyb import Timer, Pin, I2C, delay
from math import pi
import time

from discretized_estimation import RomiObserver
from imu_Driver import IMU
from Encoder_Driver import Encoder
from Motor_Driver import Motor
from Controller_Class import Controller   # your PID class

# ========== ROBOT PARAMETERS ==========
r      = 0.035   # wheel radius [m]
l      = 0.141   # wheelbase [m]
Ts_ms  = 10      # sample time [ms] (Ad,Bd at 0.01 s)

# Global “nice” units (from observer)
s_mm   = 0.0     # forward distance [mm]
a_deg  = 0.0     # heading estimate from observer [deg]

# ========== STATE-SPACE MATRICES (discrete) ==========
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

# Observer gain L
L = [
    [ 0.08, -0.08, 0.00, -0.02],  # wL
    [-0.08,  0.08, 0.00,  0.02],  # wR
    [ 0.35,  0.35, 0.00,  0.00],  # s
    [ 0.00,  0.00, 0.50,  0.70],  # psi
]

# ========== HELPERS ==========

def clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v

def wrap_deg180(a):
    # wrap angle in degrees to (-180, 180]
    while a <= -180:
        a += 360
    while a > 180:
        a -= 360
    return a

# ========== HARDWARE SETUP ==========

# Motors
tim3 = Timer(3, freq=20000)
motor_left  = Motor(Pin.cpu.A6,  Pin.cpu.C7,  Pin.cpu.B2,  tim3, 1)
motor_right = Motor(Pin.cpu.A7,  Pin.cpu.B12, Pin.cpu.B14, tim3, 2)
motor_left.enable()
motor_right.enable()

# Encoders
encoder_left  = Encoder(Timer(1, prescaler=0, period=0xFFFF), Pin.cpu.A8, Pin.cpu.A9)
encoder_right = Encoder(Timer(2, prescaler=0, period=0xFFFF), Pin.cpu.A0, Pin.cpu.A1)

# Wheel velocity controllers (your existing gains)
controller_left  = Controller(2.5, 20.0, 0.1)
controller_right = Controller(2.5, 20.0, 0.1)

# IMU
i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)
imu = IMU(i2c, addr=0x28)
delay(700)
imu.push_cal_data()
delay(100)
imu._set_mode("NDOF")
delay(100)

# Observer
obs = RomiObserver(Ad, Bd, r, l, L=L)

# IMU global reference only for observer heading
psi0_deg = imu.read_heading()

def get_imu_rel_deg():
    """IMU heading relative to psi0_deg, wrapped to (-180,180]. Used for observer."""
    global psi0_deg
    psi_abs = imu.read_heading()
    return wrap_deg180(psi_abs - psi0_deg)

# ========== CORE STEP / RESET ==========

def reset_once():
    """Zero encoders, reset observer, and set IMU reference."""
    global s_mm, a_deg, psi0_deg

    encoder_left.zero()
    encoder_right.zero()
    encoder_left.update()
    encoder_right.update()

    obs.reset()

    psi0_deg = imu.read_heading()

    s_mm  = 0.0
    a_deg = 0.0

def do_step(effL, effR):
    """
    One generic time step:
      - apply efforts
      - read sensors
      - update observer
      - update s_mm, a_deg
    """
    global s_mm, a_deg

    effL = clamp(effL, -100, 100)
    effR = clamp(effR, -100, 100)

    motor_left.set_effort(effL)
    motor_right.set_effort(effR)

    # Approximate motor voltages for observer input
    Vbatt = 7.2  # adjust to measured battery if you want
    uL = Vbatt * (effL / 100.0)
    uR = Vbatt * (effR / 100.0)
    u = np.array([[uL], [uR]])

    # Encoders
    encoder_left.update()
    encoder_right.update()
    SL = float(encoder_left.distance_traveled())   # meters since last reset
    SR = float(encoder_right.distance_traveled())

    # IMU: relative heading and yaw rate (for observer only)
    psi_rel_deg = get_imu_rel_deg()
    yaw_dps     = imu.read_yaw_rate()  # deg/s

    # Observer step
    xhat = obs.step(u, SL, SR, psi_rel_deg, yaw_dps)

    # Convert to nicer units
    s_mm  = float(xhat[2, 0]) * 1000.0
    a_deg = float(xhat[3, 0]) * (180.0 / pi)

    # Debug print
    print("xhat:", float(xhat[0,0]), float(xhat[1,0]), s_mm, a_deg)

    delay(Ts_ms)

# ========== STRAIGHT-LINE MOTION ==========

def step_straight():
    """One step of straight-line motion (velocity controlled)."""
    v_target = 10.0  # “desired encoder velocity” units

    Lgain = controller_left.update(v_target,  float(encoder_left.velocity))
    Rgain = controller_right.update(v_target, float(encoder_right.velocity))

    base_eff = 5.0
    effL = base_eff + Lgain
    effR = base_eff + Rgain

    do_step(effL, effR)

def run_straight(distance_mm, timeout_ms):
    """
    Drive forward by ~distance_mm, using observer s_mm.
    """
    global s_mm
    start_s = s_mm
    target  = distance_mm
    margin  = 5.0  # mm

    start = time.ticks_ms()
    while True:
        step_straight()
        traveled = s_mm - start_s

        if traveled >= (target - margin):
            break

        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            print("Timeout in straight")
            break

    motor_left.set_effort(0)
    motor_right.set_effort(0)

# ========== BASE TURN STEPS (effort-controlled) ==========

def step_turn_cw_base(eff):
    """
    One in-place clockwise step.
    eff > 0 is a "base effort" which gets shaped by wheel velocity controllers.
    """
    v_target = 10.0

    Lgain = controller_left.update(v_target,  float(encoder_left.velocity))
    Rgain = controller_right.update(v_target, float(encoder_right.velocity))

    eff = clamp(eff, 0, 100)

    effL =  eff + Lgain   # left forward
    effR = -(eff + Rgain) # right backward

    do_step(effL, effR)

def step_turn_ccw_base(eff):
    """
    One in-place counter-clockwise step.
    eff > 0 is a "base effort" which gets shaped by wheel velocity controllers.
    """
    v_target = 10.0

    Lgain = controller_left.update(v_target,  float(encoder_left.velocity))
    Rgain = controller_right.update(v_target, float(encoder_right.velocity))

    eff = clamp(eff, 0, 100)

    effL = -(eff + Lgain)  # left backward
    effR =  (eff + Rgain)  # right forward

    do_step(effL, effR)

# ========== IMU-BASED TURNING WITH YOUR PID CONTROLLER ==========

def _delta_yaw_cw(psi_start, psi_now):
    """
    Absolute yaw delta in degrees for a clockwise rotation.
    Assumes imu.read_heading() in [0, 360).
    Returns delta in [0, 360).
    """
    d = psi_now - psi_start
    while d < 0:
        d += 360
    while d >= 360:
        d -= 360
    return d

def _delta_yaw_ccw(psi_start, psi_now):
    """
    Absolute yaw delta in degrees for a counter-clockwise rotation.
    Assumes imu.read_heading() in [0, 360).
    Returns delta in [0, 360).
    """
    d = psi_start - psi_now
    while d < 0:
        d += 360
    while d >= 360:
        d -= 360
    return d

def run_turn_cw_imu(deg, timeout_ms):
    """
    Turn clockwise by `deg` physical degrees using the IMU + PID.
    Uses absolute heading 0–360 and its own local reference.
    """
    KP_ANG = 1.0
    KI_ANG = 0.0
    KD_ANG = 0.05
    ctrl = Controller(KP_ANG, KI_ANG, KD_ANG)

    deg = abs(deg)
    psi_start = imu.read_heading()   # absolute heading at start

    tol_stop = 2.0   # within this many degrees, we call it good
    eff_min  = 3.0
    eff_max  = 20.0

    t0 = time.ticks_ms()
    while True:
        psi_now  = imu.read_heading()
        yaw_mag  = _delta_yaw_cw(psi_start, psi_now)  # [0, 360)
        err      = deg - yaw_mag

        if err <= tol_stop:
            # close enough
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            delay(100)
            break

        # PID with your controller (uses abs(measured) inside)
        eff_cmd = ctrl.update(deg, yaw_mag)

        # Do not reverse if overshoot: just stop
        if eff_cmd <= 0:
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            delay(Ts_ms)
        else:
            # Limit effort more when close to target to reduce overshoot
            # Max effort shrinks with error
            local_eff_max = eff_min + 0.8 * err   # soft cap
            if local_eff_max > eff_max:
                local_eff_max = eff_max
            if local_eff_max < eff_min:
                local_eff_max = eff_min

            eff = clamp(eff_cmd, eff_min, local_eff_max)
            step_turn_cw_base(eff)

        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            print("Timeout in run_turn_cw_imu; yaw_mag =", yaw_mag)
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            break

def run_turn_ccw_imu(deg, timeout_ms):
    """
    Turn counter-clockwise by `deg` physical degrees using the IMU + PID.
    Uses absolute heading 0–360 and its own local reference.
    """
    KP_ANG = 1.0
    KI_ANG = 0.0
    KD_ANG = 0.05
    ctrl = Controller(KP_ANG, KI_ANG, KD_ANG)

    deg = abs(deg)
    psi_start = imu.read_heading()   # absolute heading at start

    tol_stop = 2.0
    eff_min  = 3.0
    eff_max  = 20.0

    t0 = time.ticks_ms()
    while True:
        psi_now  = imu.read_heading()
        yaw_mag  = _delta_yaw_ccw(psi_start, psi_now)  # [0, 360)
        err      = deg - yaw_mag

        if err <= tol_stop:
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            delay(100)
            break

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
            step_turn_ccw_base(eff)

        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            print("Timeout in run_turn_ccw_imu; yaw_mag =", yaw_mag)
            motor_left.set_effort(0)
            motor_right.set_effort(0)
            break

# ========== MAIN: SQUARE PATTERN ==========

reset_once()
print("START SQUARE PATTERN")

# 1) straight 300 mm
print("Phase 1: straight 300 mm")
run_straight(300.0, timeout_ms=8000)

# 2) turn 90 CW (IMU)
print("Phase 2: turn 90 CW (IMU)")
run_turn_cw_imu(90.0, timeout_ms=6000)

# 3) straight 300 mm
print("Phase 3: straight 300 mm")
run_straight(300.0, timeout_ms=8000)

# 4) turn 180 CCW (IMU)
print("Phase 4: turn 180 CCW (IMU)")
run_turn_ccw_imu(180.0, timeout_ms=9000)

# 5) straight 300 mm
print("Phase 5: straight 300 mm")
run_straight(300.0, timeout_ms=8000)

# 6) turn 90 CCW (IMU)
print("Phase 6: turn 90 CCW (IMU)")
run_turn_ccw_imu(90.0, timeout_ms=6000)

# 7) straight 300 mm
print("Phase 7: straight 300 mm")
run_straight(300.0, timeout_ms=8000)

# 8) turn 180 CW (IMU)
print("Phase 8: turn 180 CW (IMU)")
run_turn_cw_imu(180.0, timeout_ms=9000)

motor_left.set_effort(0)
motor_right.set_effort(0)
print("Finished square pattern")

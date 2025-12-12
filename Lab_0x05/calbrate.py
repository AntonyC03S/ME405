from pyb import I2C, delay
import struct, time
from imu_Driver import IMU



i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)
imu = IMU(i2c, addr=0x28)
delay(700)

imu._set_mode("NDOF")

while True:

    hi = imu.cali_status()
    print(hi)

    if hi == (3,3,3,3):
        imu.get_cal_data()
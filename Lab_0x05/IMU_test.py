from pyb import I2C
import struct, time
from imu_Driver import IMU

i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)  # start at 100 kHz

imu = IMU(i2c, addr=0x28)   # use 0x29 if ADR is high
imu.push_cal_data()
time.sleep_ms(100)
imu._set_mode("NDOF")  # set to IMU mode
time.sleep_ms(100)
print(imu.cali_status())


while True:
    heading, roll, pitch = imu.read_euler()
    print("Heading: {:.2f}, Roll: {:.2f}, Pitch: {:.2f}".format(heading, roll, pitch))
    time.sleep_ms(500)



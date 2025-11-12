from pyb import I2C
from imu_Class import IMU
import time

# Create I2C bus 2 (Y9=SCL, Y10=SDA)
i2c = I2C(2, I2C.CONTROLLER, baudrate=400000)

# Create IMU instance
imu = IMU(i2c)


# Read continuously
while True:
    acc = imu.read('Acc')
    print("Accel (m/s²):", acc)
    time.sleep(0.5)

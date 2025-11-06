from pyb import Pin, I2C
from IMU_Class import IMU

# Create I2C bus 2 (Y9=SCL, Y10=SDA)
i2c = I2C(2, I2C.CONTROLLER, baudrate=400000)

# Create IMU instance
imu = IMU(i2c)

hi = imu.read_acceleration()
print(hi)

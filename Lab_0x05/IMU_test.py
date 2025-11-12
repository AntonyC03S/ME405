from pyb import I2C
import struct, time
from imu_Driver import IMU

i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)  # start at 100 kHz
print("Scan:", i2c.scan())  # expect [40] for 0x28 or [41] for 0x29

imu = IMU(i2c, addr=0x28)   # use 0x29 if ADR is high

def bytes_to_xyz(raw6):
    x = struct.unpack('<h', raw6[0:2])[0]
    y = struct.unpack('<h', raw6[2:4])[0]
    z = struct.unpack('<h', raw6[4:6])[0]
    return x, y, z

while True:
    acc_raw  = imu.read('acc')   # 6 bytes
    gyro_raw = imu.read('gyro')
    mag_raw  = imu.read('mag')

    ax, ay, az = bytes_to_xyz(acc_raw)   # scale later as needed
    gx, gy, gz = bytes_to_xyz(gyro_raw)
    mx, my, mz = bytes_to_xyz(mag_raw)

    print("ACC raw:", (ax, ay, az), "  GYRO raw:", (gx, gy, gz), "  MAG raw:", (mx, my, mz))
    time.sleep(0.2)


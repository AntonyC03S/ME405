from pyb import Pin, I2C, delay

class IMU:
    def __init__(self, i2c: I2C, addr: int = 0x28):
        self._i2c = i2c
        self._addr = addr
        self._i2c.init(I2C.CONTROLLER, baudrate=400_000)

    def read_acceleration(self):
        # Read 6 bytes of acceleration data
        data = self._i2c.mem_read(6, self._addr, 0x28 | 0x80)
        ax = int.from_bytes(data[0:2], 'little', signed=True)
        ay = int.from_bytes(data[2:4], 'little', signed=True)
        az = int.from_bytes(data[4:6], 'little', signed=True)
        return (ax, ay, az)



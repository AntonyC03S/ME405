from pyb import I2C, delay

class IMU:
    def __init__(self, i2c: I2C, addr: int = 0x28):
        self._i2c, self._addr = i2c, addr
        self._i2c.init(I2C.CONTROLLER, baudrate=400_000)

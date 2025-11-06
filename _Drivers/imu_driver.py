from pyb import I2C

class IMU:
    
    def __init__(self, I2C):
        self.i2c = I2C
        self.devad = 0x28

        #Read 8-bit config data from reg and write 1100 to lower 4 bits to set ndof mode
        self.config = self.i2c.mem_read(1, self.devad, 0x3D)
        self.higher_4_bits = self.config & 0xF0
        self.result = self.higher_4_bits | 0x0b
        self.i2c.mem_write(self.result, self.devad, 0x3D)

    def read(self,DATA):
        if DATA == 'Gyro':
            self.gyrobuf = bytearray(0 for n in range(6))
            gyrodata = self.i2c.mem_read(self.gyrobuf, self.devad, 0x14)
            return gyrodata
        elif DATA == 'Acc':
            self.accbuf = bytearray(0 for n in range(6))
            accdata = self.i2c.mem_read(self.magbuf, self.devad, 0x08)
            return accdata
        elif DATA == 'MAG':
            self.magbuf = bytearray(0 for n in range(6))
            magdata = self.i2c.mem_read(self.magbuf, self.devad, 0x0E)
            return magdata


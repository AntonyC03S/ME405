from pyb import I2C
import time

class IMU:
    # Registers
    OPR_MODE_REG   = 0x3D
    PWR_MODE_REG   = 0x3E
    SYS_TRIGGER_REG= 0x3F
    CHIP_ID_REG    = 0x00

    # Data registers (LSB of X for each block)
    ACC_DATA_X_LSB = 0x08
    MAG_DATA_X_LSB = 0x0E
    GYRO_DATA_X_LSB= 0x14

    # Modes
    CONFIG_MODE = 0x00
    NDOF_MODE   = 0x0C  # <- correct NDOF

    def __init__(self, i2c, addr=0x28):
        self.i2c = i2c
        self.devad = addr  # 0x29 if ADR pulled high

        # OPTIONAL: verify chip ID (0xA0)
        try:
            cid = self.i2c.mem_read(1, self.devad, self.CHIP_ID_REG)[0]
        except OSError:
            raise RuntimeError("I2C read failed. Check wiring/bus/address.")
        if cid != 0xA0:
            raise RuntimeError("BNO055 not found/ready. Chip ID: 0x{:02X}".format(cid))

        # Enter CONFIG before changing op mode
        self._set_mode(self.CONFIG_MODE)
        time.sleep_ms(25)

        # (Optional) soft reset to be clean
        self.i2c.mem_write(bytes([0x20]), self.devad, self.SYS_TRIGGER_REG)
        time.sleep_ms(700)

        # Back to normal power
        self.i2c.mem_write(bytes([0x00]), self.devad, self.PWR_MODE_REG)
        time.sleep_ms(10)

        # Enter NDOF
        self._set_mode(self.NDOF_MODE)
        time.sleep_ms(20)

    def _set_mode(self, mode):
        self.i2c.mem_write(bytes([mode]), self.devad, self.OPR_MODE_REG)

    def scan(self):
        return self.i2c.scan()

    def read(self, DATA):
        DATA = DATA.lower()
        if DATA == 'gyro':
            # return 6 raw bytes (xL,xH,yL,yH,zL,zH)
            return self.i2c.mem_read(6, self.devad, self.GYRO_DATA_X_LSB)
        elif DATA == 'acc':
            return self.i2c.mem_read(6, self.devad, self.ACC_DATA_X_LSB)
        elif DATA == 'mag':
            return self.i2c.mem_read(6, self.devad, self.MAG_DATA_X_LSB)
        else:
            raise ValueError("Unknown data type: {}".format(DATA))



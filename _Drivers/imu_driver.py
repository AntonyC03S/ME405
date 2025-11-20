from pyb import I2C
import time
import struct

class IMU:
    # Registers
    OPR_MODE_REG   = 0x3D
    PWR_MODE_REG   = 0x3E
    SYS_TRIGGER_REG= 0x3F
    CHIP_ID_REG    = 0x00
    PAGE_ID_REG = 0x07


    # Data registers (LSB of X for each block)
    ACC_DATA_X_LSB = 0x08
    MAG_DATA_X_LSB = 0x0E
    GYRO_DATA_X_LSB= 0x14
    EULER_H_LSB    = 0x1A
    CAL_DATA_LSB   = 0x55

    # Modes
    CONFIG_MODE = 0x00
    NDOF_MODE   = 0x0C 
    IMU_MODE    = 0x08

    def __init__(self, i2c, addr=0x28):
        self.i2c = i2c
        self.devad = addr
        self._set_mode("CONFIG")

    def _set_mode(self, mode):
        if mode == "NDOF":
            mode = self.NDOF_MODE
        elif mode == "CONFIG":
            mode = self.CONFIG_MODE
        elif mode == "IMU":
            mode = self.IMU_MODE

        # make sure we’re on register page 0 before touching OPR_MODE
        self.i2c.mem_write(bytes([0x00]), self.devad, self.PAGE_ID_REG)
        time.sleep_ms(10)

        self.i2c.mem_write(bytes([mode]), self.devad, self.OPR_MODE_REG)
        time.sleep_ms(25)



    def cali_status(self):
        """Return calibration status as a tuple: (sys, gyro, acc, mag)"""
        cal_stat = self.i2c.mem_read(1, self.devad, 0x35)[0]
        sys = (cal_stat >> 6) & 0x03
        gyro = (cal_stat >> 4) & 0x03
        acc = (cal_stat >> 2) & 0x03
        mag = cal_stat & 0x03
        return (sys, gyro, acc, mag)

    def read_euler(self):
        raw = self.i2c.mem_read(6, self.devad, self.EULER_H_LSB)  # EULER_H_LSB
        heading = struct.unpack('<h', raw[0:2])[0] / 16.0
        roll    = struct.unpack('<h', raw[2:4])[0] / 16.0
        pitch   = struct.unpack('<h', raw[4:6])[0] / 16.0
        return heading, roll, pitch
    
    def read_heading(self):
        raw = self.i2c.mem_read(2, self.devad, self.EULER_H_LSB)  # EULER_H_LSB
        heading = struct.unpack('<h', raw[0:2])[0] / 16.0
        return heading
    
    def get_cal_data(self, filename="cal_data.bin"):
        # remember current mode
        prev = self.i2c.mem_read(1, self.devad, self.OPR_MODE_REG)[0]

        # go to CONFIG, make sure we're on page 0
        self.i2c.mem_write(bytes([self.CONFIG_MODE]), self.devad, self.OPR_MODE_REG)
        time.sleep_ms(25)
        self.i2c.mem_write(bytes([0x00]), self.devad, self.PAGE_ID_REG)
        time.sleep_ms(5)

        # read 22 bytes: 0x55..0x6A (offsets + radii)
        data = self.i2c.mem_read(22, self.devad, 0x55)

        # save to file (binary so you can restore later)
        with open(filename, 'wb') as f:
            f.write(data)

        # restore previous mode
        self.i2c.mem_write(bytes([prev]), self.devad, self.OPR_MODE_REG)
        time.sleep_ms(25)

        return data  # optional: so you can print/inspect


    def push_cal_data(self):
        filename = "cal_data.bin"
        with open(filename, 'rb') as f:
        # Read the entire file content as bytes
            file_content_bytes = f.read()

        # Convert the bytes object to a bytearray and pastes to cal data lsb
        cal_data_old = bytearray(file_content_bytes)
        self.i2c.mem_write(cal_data_old,self.devad, self.CAL_DATA_LSB)

    def read_gyro(self):
        """Return (gx, gy, gz) in deg/s."""
        raw = self.i2c.mem_read(6, self.devad, self.GYRO_DATA_X_LSB)
        gx = struct.unpack('<h', raw[0:2])[0] / 16.0
        gy = struct.unpack('<h', raw[2:4])[0] / 16.0
        gz = struct.unpack('<h', raw[4:6])[0] / 16.0
        return gx, gy, gz

    def read_yaw_rate(self):
        """Return yaw rate (gz) in deg/s."""
        # GYRO_DATA_X_LSB = 0x14, Y=0x16, Z=0x18
        GYRO_Z_LSB = 0x18
        raw = self.i2c.mem_read(2, self.devad, GYRO_Z_LSB)
        yaw_rate = struct.unpack('<h', raw)[0] / 16.0
        return yaw_rate  # degrees per second





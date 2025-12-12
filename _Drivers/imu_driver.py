"""! @file imu_driver.py
@brief I2C interface for a BNO055 IMU sensor.

The IMU driver is used to read the heading, roll, pitch and gyro data. 
"""

from pyb import I2C  # type: ignore
import time
import struct


class IMU:
    """! BNO055 IMU driver over I2C.

    @brief Wraps common BNO055 functions such as mode switching, calibration,
    and reading Euler angles / gyro data.

    """

    # Register addresses
    OPR_MODE_REG    = 0x3D
    PWR_MODE_REG    = 0x3E
    SYS_TRIGGER_REG = 0x3F
    CHIP_ID_REG     = 0x00
    PAGE_ID_REG     = 0x07
    ACC_DATA_X_LSB  = 0x08
    MAG_DATA_X_LSB  = 0x0E
    GYRO_DATA_X_LSB = 0x14
    EULER_H_LSB     = 0x1A
    CAL_DATA_LSB    = 0x55

    # Operation modes
    CONFIG_MODE = 0x00
    NDOF_MODE   = 0x0C
    IMU_MODE    = 0x08

    def __init__(self, i2c: I2C, addr: int = 0x28):
        """! Initialize an IMU instance.

        @param i2c   Initialized I2C object.
        @param addr  7-bit I2C address of the BNO055 (default: 0x28).
        """
        self.i2c = i2c
        self.devad = addr
        self._set_mode("CONFIG")

    def _set_mode(self, mode: str) -> None:
        """! Internal helper to switch IMU operation mode.

        @param mode String specifying mode: `"CONFIG"`, `"NDOF"`, or `"IMU"`.

        """
        if mode == "NDOF":
            mode_val = self.NDOF_MODE
        elif mode == "CONFIG":
            mode_val = self.CONFIG_MODE
        elif mode == "IMU":
            mode_val = self.IMU_MODE
        else:
            mode_val = self.CONFIG_MODE

        self.i2c.mem_write(bytes([0x00]), self.devad, self.PAGE_ID_REG)
        time.sleep_ms(10)

        self.i2c.mem_write(bytes([mode_val]), self.devad, self.OPR_MODE_REG)
        time.sleep_ms(25)

    def cali_status(self):
        """! Get IMU calibration status.

        @brief Returns the calibration state of system, gyro, accelerometer,
        and magnetometer.

        @return Tuple `(sys, gyro, acc, mag)` where each value is from 0-3.
        A value of 3 indicates fully calibrated.
        """
        cal_stat = self.i2c.mem_read(1, self.devad, 0x35)[0]
        sys = (cal_stat >> 6) & 0x03
        gyro = (cal_stat >> 4) & 0x03
        acc = (cal_stat >> 2) & 0x03
        mag = cal_stat & 0x03
        return (sys, gyro, acc, mag)

    def read_euler(self):
        """! Read Euler angles from the IMU.

        @brief Returns heading, roll, and pitch in degrees.

        @return Tuple `(heading, roll, pitch)` in degrees.

        """
        raw = self.i2c.mem_read(6, self.devad, self.EULER_H_LSB)
        heading = struct.unpack('<h', raw[0:2])[0] / 16.0
        roll    = struct.unpack('<h', raw[2:4])[0] / 16.0
        pitch   = struct.unpack('<h', raw[4:6])[0] / 16.0
        return heading, roll, pitch

    def read_heading(self) -> float:
        """! Read only the heading (yaw) angle.

        @return Heading in degrees.
        """
        raw = self.i2c.mem_read(2, self.devad, self.EULER_H_LSB)
        heading = struct.unpack('<h', raw[0:2])[0] / 16.0
        return heading

    def get_cal_data(self, filename: str = "cal_data.bin"):
        """! Read and store calibration data to a file.

        @brief Switches to CONFIG mode, reads calibration data, and writes
        it to a binary file for later reuse.

        @param filename Name of the file where calibration data is saved.
                        Default is `"cal_data.bin"`.

        @return The raw calibration data as a bytes object.
        """
        # Save current mode
        prev = self.i2c.mem_read(1, self.devad, self.OPR_MODE_REG)[0]

        # Switch to config mode and page 0
        self.i2c.mem_write(bytes([self.CONFIG_MODE]), self.devad, self.OPR_MODE_REG)
        time.sleep_ms(25)
        self.i2c.mem_write(bytes([0x00]), self.devad, self.PAGE_ID_REG)
        time.sleep_ms(5)

        # Read 22 bytes of calibration data from 0x55
        data = self.i2c.mem_read(22, self.devad, self.CAL_DATA_LSB)

        # Store to file
        with open(filename, "wb") as f:
            f.write(data)

        # Restore previous mode
        self.i2c.mem_write(bytes([prev]), self.devad, self.OPR_MODE_REG)
        time.sleep_ms(25)

        return data

    def push_cal_data(self, filename: str = "cal_data.bin") -> None:
        """! Push stored calibration data into the IMU.

        @brief Reads calibration data from a file and writes it to the IMU.

        @param filename File containing previously saved calibration data
                       (default: `"cal_data.bin"`).

        This can be used at startup to restore a known good calibration,
        avoiding re-calibration on every power cycle.
        """
        with open(filename, "rb") as f:
            file_content_bytes = f.read()

        cal_data = bytearray(file_content_bytes)
        self.i2c.mem_write(cal_data, self.devad, self.CAL_DATA_LSB)

    def read_gyro(self):
        """! Read gyroscope rates for all three axes.

        @brief Reads raw gyro data from the IMU and converts it to deg/s.

        @return Tuple `(gx, gy, gz)` in degrees per second.
        """
        raw = self.i2c.mem_read(6, self.devad, self.GYRO_DATA_X_LSB)
        gx = struct.unpack('<h', raw[0:2])[0] / 16.0
        gy = struct.unpack('<h', raw[2:4])[0] / 16.0
        gz = struct.unpack('<h', raw[4:6])[0] / 16.0
        return gx, gy, gz

    def read_yaw_rate(self) -> float:
        """! Read yaw rate from the gyroscope.

        @brief Returns the Z-axis gyro rate.

        @return Yaw rate (gz) in degrees per second.
        """
        GYRO_Z_LSB = 0x18
        raw = self.i2c.mem_read(2, self.devad, GYRO_Z_LSB)
        yaw_rate = struct.unpack('<h', raw)[0] / 16.0
        return yaw_rate

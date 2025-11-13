from pyb import I2C
import time
import struct

class IMU:
    # BNO055 Registers
    CHIP_ID_REG = 0x00
    OPR_MODE_REG = 0x3D
    PWR_MODE_REG = 0x3E
    SYS_TRIGGER_REG = 0x3F
    
    # Operation Modes
    CONFIG_MODE = 0x00
    NDOF_MODE = 0x0C
    
    # Data Registers
    ACC_DATA_X_LSB = 0x08
    MAG_DATA_X_LSB = 0x0E
    GYRO_DATA_X_LSB = 0x14
    EULER_H_LSB = 0x1A
    CAL_DATA_LSB = 0x55
    
    def __init__(self, i2c):
        self.i2c = i2c
        self.devad = 0x28
        
        #Initialize sensor
        self._init_sensor()
    
    def _init_sensor(self):
        """Initialize the BNO055 sensor"""
        # Set to config mode
        self.i2c.mem_write(bytes([self.CONFIG_MODE]), self.devad, self.OPR_MODE_REG)
        
        # Reset system
        self.i2c.mem_write(bytes([0x20]), self.devad, self.SYS_TRIGGER_REG)
        
        # Set to normal power mode
        self.i2c.mem_write(bytes([0x00]), self.devad, self.PWR_MODE_REG)

        try:
            self.push_cal_data()
        
        except:
            check = self.get_cal_status()
            if check == [3,3,3,3]:
                self.get_cal_data()
                self.push_cal_data()
            else:
                 # Set to NDOF mode (fusion mode with all sensors)
                self.i2c.mem_write(bytes([self.NDOF_MODE]), self.devad, self.OPR_MODE_REG)
    
    def set_mode(self, mode):
        """Set operation mode"""
        self.i2c.mem_write(bytes([mode]), self.devad, self.OPR_MODE_REG)
    
    def scan(self):
        """Scan I2C bus for devices"""
        return self.i2c.scan()
    
    def read(self, DATA):
        """Read sensor data"""
        if DATA == 'Gyro':
            raw_data = self.i2c.mem_read(6, self.devad, self.GYRO_DATA_X_LSB)
            return self._parse_sensor_data(raw_data, scale=16.0)  # LSB = 1/16 dps
            
        elif DATA == 'Acc':
            raw_data = self.i2c.mem_read(6, self.devad, self.ACC_DATA_X_LSB)
            return self._parse_sensor_data(raw_data, scale=100.0)  # LSB = 1/100 m/s²
            
        elif DATA == 'Mag':
            raw_data = self.i2c.mem_read(6, self.devad, self.MAG_DATA_X_LSB)
            return self._parse_sensor_data(raw_data, scale=16.0)  # LSB = 1/16 µT
            
        elif DATA == 'Euler':
            raw_data = self.i2c.mem_read(6, self.devad, self.EULER_H_LSB)
            return self._parse_sensor_data(raw_data, scale=16.0)  # LSB = 1/16 degrees
        
        else:
            raise ValueError(f"Unknown data type: {DATA}")
    
    def _parse_sensor_data(self, raw_data, scale=1.0):
        """Parse 6 bytes of sensor data into x, y, z values"""
        # Convert bytes to signed 16-bit integers (little-endian)
        x = struct.unpack('<h', raw_data[0:2])[0] / scale
        y = struct.unpack('<h', raw_data[2:4])[0] / scale
        z = struct.unpack('<h', raw_data[4:6])[0] / scale
        return (x, y, z)
    
    def get_cal_status(self):
        """Get calibration status for system, gyro, accel, mag (0-3 each)"""
        calib_stat = self.i2c.mem_read(1, self.devad, 0x35)[0]
        sys = (calib_stat >> 6) & 0x03
        gyro = (calib_stat >> 4) & 0x03
        accel = (calib_stat >> 2) & 0x03
        mag = calib_stat & 0x03
        return [sys,gyro,accel,mag]
    
    def get_cal_data(self):
        # Define the filename and content
        filename = "cal_data.txt"
        buf = bytearray(18)
        self.i2c.mem_read(buf, self.devad, self.CAL_DATA_LSB)

        # Open the file in write mode ('w') and write the content
        with open(filename, 'wb') as file:
            file.write(buf)

    def push_cal_data(self):
        filename = "cal_data.txt"
        with open(filename, 'rb') as f:
        # Read the entire file content as bytes
            file_content_bytes = f.read()

        # Convert the bytes object to a bytearray and pastes to cal data lsb
        cal_data_old = bytearray(file_content_bytes)
        self.i2c.mem_write(cal_data_old,self.devad, self.CAL_DATA_LSB)

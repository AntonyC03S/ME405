from pyb import Pin, ADC # type: ignore
from os import listdir
import math


class Line: 
    
    def __init__(self):
        self._white_cal = None
        self._black_cal = None
        
    def define_8(self, s1: Pin, s3: Pin, s5: Pin, s7: Pin, s9: Pin, s11: Pin, s13: Pin, s15: Pin):
        self._s1_pin = Pin(s1, mode = Pin.IN)
        self._s3_pin = Pin(s3, mode = Pin.IN)
        self._s5_pin = Pin(s5, mode = Pin.IN)
        self._s7_pin = Pin(s7, mode = Pin.IN)
        self._s9_pin = Pin(s9, mode = Pin.IN)
        self._s11_pin = Pin(s11, mode = Pin.IN)
        self._s13_pin = Pin(s13, mode = Pin.IN)
        self._s15_pin = Pin(s15, mode = Pin.IN)

        self._sensors = [ADC(self._s1_pin), ADC(self._s3_pin), 
                         ADC(self._s5_pin), ADC(self._s7_pin), 
                         ADC(self._s9_pin), ADC(self._s11_pin),
                         ADC(self._s13_pin), ADC(self._s15_pin)]
        
        self.positions = [1, 3, 5, 7, 9, 11, 13, 15]

    def define_13(self, s2: Pin, s3: Pin, s4: Pin, s5: Pin, s6: Pin, s7: Pin, s8: Pin, s9: Pin, s10: Pin, s11: Pin, s12: Pin, s13: Pin, s14: Pin):
        self._s2_pin = Pin(s2, mode = Pin.IN)
        self._s3_pin = Pin(s3, mode = Pin.IN)
        self._s4_pin = Pin(s4, mode = Pin.IN)
        self._s5_pin = Pin(s5, mode = Pin.IN)
        self._s6_pin = Pin(s6, mode = Pin.IN)
        self._s7_pin = Pin(s7, mode = Pin.IN)
        self._s8_pin = Pin(s8, mode = Pin.IN)
        self._s9_pin = Pin(s9, mode = Pin.IN)
        self._s10_pin = Pin(s10, mode = Pin.IN)
        self._s11_pin = Pin(s11, mode = Pin.IN)
        self._s12_pin = Pin(s12, mode = Pin.IN)
        self._s13_pin = Pin(s13, mode = Pin.IN)
        self._s14_pin = Pin(s14, mode = Pin.IN)

        self._sensors = [ADC(self._s2_pin), 
                         ADC(self._s3_pin), ADC(self._s4_pin),
                         ADC(self._s5_pin), ADC(self._s6_pin),
                         ADC(self._s7_pin), ADC(self._s8_pin),
                         ADC(self._s9_pin), ADC(self._s10_pin),
                         ADC(self._s11_pin), ADC(self._s12_pin),
                         ADC(self._s13_pin), ADC(self._s14_pin)]
        
        self.positions = [2,3,4,5,6,7,8,9,10,11,12,13,14]


    def cali_white(self):
        self._white_cal = [adc.read() for adc in self._sensors]
        return self._white_cal

    def cali_black(self):
        self._black_cal = [adc.read() for adc in self._sensors]
        return self._black_cal

    
    def update(self):
        values = self.readings()

        centroid_max = 15
        centroid_min = 1

        centroid_middle = 8
        numerator = 0
        denominator = 0
        
        for i in range(len(values)):
            numerator += values[i] * self.positions[i]
            denominator += values[i]
        
        if denominator == 0:
            return centroid_middle  
        
        centroid = numerator / denominator
        # centroid *= 2 
        if centroid > centroid_max:
            return centroid_max
        elif centroid < centroid_min:
            return centroid_min
        return centroid

    def readings(self):
        return [self.color_def(abs(self.calibrate(adc.read(),idx)-1)) for idx, adc in enumerate(self._sensors)]


    """--------------------Helping Functions---------------------------------"""
    
    # For Update and readings
    def calibrate(self, value, idx):
        if self._white_cal is None or self._black_cal is None:
            filelist = listdir()
            if "calibration.txt" in filelist:
                # Calibration data is present
                print("Found calibration data, skipping calibration")
                with open("calibration.txt", "r") as file:
                    # Read data from file, strip special characters, split on commas, assign
                    # to variables. Similar to HW 0x00 using file.readline()
                    lines = file.readlines()
                    self._white_cal = [int(x) for x in eval(lines[0])]
                    self._black_cal = [int(x) for x in eval(lines[1])]
            else:
                # Calibration data is not present
                input("Accept Black?")
                
                self.cali_black()
                input("Accept White?")

                self.cali_white()
                with open("calibration.txt", "w") as file:
                # Convert calibration values to strings, join with commas, append newline
                # and write to file. Essentially the inverse of HW 0x00, so use file.write()
                    file.write(", ".join(str(item) for item in self._white_cal))
                    file.write("\n")
                    file.write(", ".join(str(item) for item in self._black_cal))

        return (self._black_cal[idx] - value) / (self._black_cal[idx] - self._white_cal[idx])
    
    def color_def(self, value):
        if value > 0.006:
            return round(value,3)
        else:
            return 0



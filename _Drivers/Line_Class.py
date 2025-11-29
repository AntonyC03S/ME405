from pyb import Pin, ADC # type: ignore
from os import listdir


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

    def define_13(self, s1: Pin, s2: Pin, s3: Pin, s4: Pin, s5: Pin, s6: Pin, s7: Pin, s8: Pin, s9: Pin, s10: Pin, s11: Pin, s12: Pin, s13: Pin, s14: Pin, s15: Pin):
        self._s1_pin = Pin(s1, mode = Pin.IN)
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
        self._s15_pin = Pin(s15, mode = Pin.IN)

        self._sensors = [ADC(self._s1_pin), ADC(self._s2_pin), 
                         ADC(self._s3_pin), ADC(self._s4_pin),
                         ADC(self._s5_pin), ADC(self._s6_pin),
                         ADC(self._s7_pin), ADC(self._s8_pin),
                         ADC(self._s9_pin), ADC(self._s10_pin),
                         ADC(self._s11_pin), ADC(self._s12_pin),
                         ADC(self._s13_pin), ADC(self._s14_pin),
                         ADC(self._s15_pin)]


    def cali_white(self):
        self._white_cal = [adc.read() for adc in self._sensors]
        return self._white_cal

    def cali_black(self):
        self._black_cal = [adc.read() for adc in self._sensors]
        return self._black_cal

    
    def update(self):
        values = [self.calibrate(adc.read(),idx) for idx, adc in enumerate(self._sensors)]
        centroid_max = 18
        centroid_min = 14
        centroid_middle = 16

        # Case: No line showing
        if self.filter_val(values):
            return centroid_middle
        
        # Case: Line Edge 
        edge_case, centroid = self.edge_val(values, centroid_min, centroid_max)
        if edge_case:
            return centroid

        # Case: Line in Middle 
        positions = [1, 3, 5, 7, 9, 11, 13, 15]
        
        numerator = 0
        denominator = 0
        
        for i in range(len(values)):
            numerator += values[i] * positions[i]
            denominator += values[i]
        
        if denominator == 0:
            return centroid_middle  
        
        centroid = numerator / denominator
        centroid *= 2 
        if centroid > centroid_max:
            return centroid_max
        elif centroid < centroid_min:
            return centroid_min
        return centroid

    def readings(self):
        values = [self.calibrate(adc.read(),idx) for idx, adc in enumerate(self._sensors)]
        return values


    """--------------------Helping Functions---------------------------------"""
    # For Update
    def filter_val(self, values):
        max = 1000000          
        min = 0                  
        for i in values:
            if i > max:
                max = i
            elif i < min:
                min = i 
        
        if max - min < 100:        # 100 can be tuned
            return True
        else:
            return False
        
    # For Update
    def edge_val(self, values, centroid_min, centroid_max):
        if values[0] > values[1] and values[0] > values[2]:
            return True, centroid_min
        elif values[-1] > values[-2] and values[-1] > values[-3]:
            return True, centroid_max
        return False, 0
    
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


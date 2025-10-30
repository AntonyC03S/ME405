from pyb import Pin, ADC

class Line:
    
    def __init__(self, s1: Pin, s3: Pin, s5: Pin, s7: Pin, s9: Pin, s11: Pin, s13: Pin, s15: Pin):
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
        self._white_cal = None
        self._black_cal = None

    def cali_white(self):
        self._white_cal = [adc.read() for adc in self._sensors]
        return self._white_cal

    def cali_black(self):
        self._black_cal = [adc.read() for adc in self._sensors]
        return self._black_cal
    
    def update(self):
        values = [adc.read() for adc in self._sensors]
        
        positions = [1, 3, 5, 7, 9, 11, 13, 15]
        
        numerator = 0
        denominator = 0
        
        for i in range(len(values)):
            numerator += values[i] * positions[i]
            denominator += values[i]
        
        if denominator == 0:
            return 8  
        
        centroid = numerator / denominator
        return centroid-8


"""! @file line.py
@brief Line sensor array driver using analog reflectance sensors.

This module provides the :class:`Line` class to handle an array of
line sensors (e.g. reflectance sensors) connected to ADC pins.

Features:
- Supports 8- or 13-sensor configurations
- Per-sensor black/white calibration with file storage
- Normalized sensor readings
- Centroid computation for line-following control
"""

from pyb import Pin, ADC  # type: ignore
from os import listdir
import math  # noqa: F401 (may be used later)


class Line:
    """! Line sensor array interface.

    @brief Manages multiple analog reflectance sensors to detect and track
    a line on the ground.

    The class supports two common layouts:

    - 8-sensor configuration (`define_8`)
    - 13-sensor configuration (`define_13`)

    After calibration, the class can:
    - Return normalized sensor readings
    - Compute a centroid position of the line across the array
    """

    def __init__(self):
        """! Initialize an empty Line object.

        Calibration data and sensors are set up later via @ref define_8
        or @ref define_13 and the calibration methods.
        """
        self._white_cal = None
        self._black_cal = None
        self._sensors = []
        self.positions = []

    def define_8(
        self,
        s1: Pin,
        s3: Pin,
        s5: Pin,
        s7: Pin,
        s9: Pin,
        s11: Pin,
        s13: Pin,
        s15: Pin,
    ) -> None:
        """! Configure an 8-sensor line array.

        @brief Sets up 8 ADC sensors on the given pins and their position indices.

        @param s1   Pin for sensor at position 1.
        @param s3   Pin for sensor at position 3.
        @param s5   Pin for sensor at position 5.
        @param s7   Pin for sensor at position 7.
        @param s9   Pin for sensor at position 9.
        @param s11  Pin for sensor at position 11.
        @param s13  Pin for sensor at position 13.
        @param s15  Pin for sensor at position 15.
        """
        self._s1_pin = Pin(s1, mode=Pin.IN)
        self._s3_pin = Pin(s3, mode=Pin.IN)
        self._s5_pin = Pin(s5, mode=Pin.IN)
        self._s7_pin = Pin(s7, mode=Pin.IN)
        self._s9_pin = Pin(s9, mode=Pin.IN)
        self._s11_pin = Pin(s11, mode=Pin.IN)
        self._s13_pin = Pin(s13, mode=Pin.IN)
        self._s15_pin = Pin(s15, mode=Pin.IN)

        self._sensors = [
            ADC(self._s1_pin),
            ADC(self._s3_pin),
            ADC(self._s5_pin),
            ADC(self._s7_pin),
            ADC(self._s9_pin),
            ADC(self._s11_pin),
            ADC(self._s13_pin),
            ADC(self._s15_pin),
        ]

        # Logical positions corresponding to each sensor
        self.positions = [1, 3, 5, 7, 9, 11, 13, 15]

    def define_13(
        self,
        s2: Pin,
        s3: Pin,
        s4: Pin,
        s5: Pin,
        s6: Pin,
        s7: Pin,
        s8: Pin,
        s9: Pin,
        s10: Pin,
        s11: Pin,
        s12: Pin,
        s13: Pin,
        s14: Pin,
    ) -> None:
        """! Configure a 13-sensor line array.

        @brief Sets up 13 ADC sensors on the given pins and their position indices.

        @param s2   Pin for sensor at position 2.
        @param s3   Pin for sensor at position 3.
        @param s4   Pin for sensor at position 4.
        @param s5   Pin for sensor at position 5.
        @param s6   Pin for sensor at position 6.
        @param s7   Pin for sensor at position 7.
        @param s8   Pin for sensor at position 8.
        @param s9   Pin for sensor at position 9.
        @param s10  Pin for sensor at position 10.
        @param s11  Pin for sensor at position 11.
        @param s12  Pin for sensor at position 12.
        @param s13  Pin for sensor at position 13.
        @param s14  Pin for sensor at position 14.
        """
        self._s2_pin = Pin(s2, mode=Pin.IN)
        self._s3_pin = Pin(s3, mode=Pin.IN)
        self._s4_pin = Pin(s4, mode=Pin.IN)
        self._s5_pin = Pin(s5, mode=Pin.IN)
        self._s6_pin = Pin(s6, mode=Pin.IN)
        self._s7_pin = Pin(s7, mode=Pin.IN)
        self._s8_pin = Pin(s8, mode=Pin.IN)
        self._s9_pin = Pin(s9, mode=Pin.IN)
        self._s10_pin = Pin(s10, mode=Pin.IN)
        self._s11_pin = Pin(s11, mode=Pin.IN)
        self._s12_pin = Pin(s12, mode=Pin.IN)
        self._s13_pin = Pin(s13, mode=Pin.IN)
        self._s14_pin = Pin(s14, mode=Pin.IN)

        self._sensors = [
            ADC(self._s2_pin),
            ADC(self._s3_pin),
            ADC(self._s4_pin),
            ADC(self._s5_pin),
            ADC(self._s6_pin),
            ADC(self._s7_pin),
            ADC(self._s8_pin),
            ADC(self._s9_pin),
            ADC(self._s10_pin),
            ADC(self._s11_pin),
            ADC(self._s12_pin),
            ADC(self._s13_pin),
            ADC(self._s14_pin),
        ]

        self.positions = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    def cali_white(self):
        """! Capture white calibration values.

        @brief Reads all sensors and stores their values as the "white" reference.

        @return List of raw ADC values measured over a white surface.
        """
        self._white_cal = [adc.read() for adc in self._sensors]
        return self._white_cal

    def cali_black(self):
        """! Capture black calibration values.

        @brief Reads all sensors and stores their values as the "black" reference.

        @return List of raw ADC values measured over a black (line) surface.
        """
        self._black_cal = [adc.read() for adc in self._sensors]
        return self._black_cal

    def update(self) -> float:
        """! Compute line position using centroid.

        @brief Uses normalized sensor readings to compute a weighted average
        of sensor positions, yielding an estimated line position.

        @return Centroid position as a float in the same index space as
                @ref positions (e.g. between 1 and 15 for an 8-sensor setup).
        """
        values = self.readings()

        centroid_max = 15
        centroid_min = 1
        centroid_middle = 8

        numerator = 0.0
        denominator = 0.0

        for i in range(len(values)):
            numerator += values[i] * self.positions[i]
            denominator += values[i]

        # If all sensors read zero, assume line is centered
        if denominator == 0:
            return centroid_middle

        centroid = numerator / denominator

        if centroid > centroid_max:
            return centroid_max
        elif centroid < centroid_min:
            return centroid_min

        return centroid

    def readings(self):
        """! Get normalized sensor readings.

        @brief Returns a list of calibrated, thresholded sensor values.

        Each value is:
        - Calibrated between black and white references
        - Flipped so higher value means "darker" (more line)
        - Thresholded such that very small values are set to 0

        @return List of floats in approximately [0, 1].
        """
        return [
            self.color_def(abs(self.calibrate(adc.read(), idx) - 1))
            for idx, adc in enumerate(self._sensors)
        ]


    def calibrate(self, value: int, idx: int) -> float:
        """! Map raw ADC value into a normalized range [0, 1].

        @brief Uses stored black/white calibration values to normalize a reading.

        @param value Raw ADC reading for a single sensor.
        @param idx   Index of the sensor in the array.
        @return Normalized value between 0 (white) and 1 (black).
        """
        # Lazy-load calibration from file if needed
        if self._white_cal is None or self._black_cal is None:
            filelist = listdir()
            if "calibration.txt" in filelist:
                # Calibration data is present
                print("Found calibration data, skipping calibration")
                with open("calibration.txt", "r") as file:
                    lines = file.readlines()
                    self._white_cal = [int(x) for x in eval(lines[0])]
                    self._black_cal = [int(x) for x in eval(lines[1])]
            else:
                # Calibration data is not present; do interactive calibration
                input("Accept Black?")
                self.cali_black()
                input("Accept White?")
                self.cali_white()

                with open("calibration.txt", "w") as file:
                    file.write(", ".join(str(item) for item in self._white_cal))
                    file.write("\n")
                    file.write(", ".join(str(item) for item in self._black_cal))

        return (self._black_cal[idx] - value) / (
            self._black_cal[idx] - self._white_cal[idx]
        )

    def color_def(self, value: float) -> float:
        """! Threshold and round a normalized sensor value.

        @param value Normalized raw value (typically in [0, 1]).
        @return Zero if below a small threshold, otherwise the rounded value.
        """
        if value > 0.006:
            return round(value, 3)
        else:
            return 0.0

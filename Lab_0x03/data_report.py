import csv
import os
import matplotlib.pylab as plt
import math
import numpy as np

def main():
    folder_path = os.path.join("Lab_0x03", "data")
    plt.figure()
    motor_gain_speed = []
    # Loop through each CSV file in the folder
    for filename in sorted(os.listdir(folder_path)):
        left_speed = []
        right_speed = []
        left_poistion = []
        right_poistion = []
        time  = []
        motor_gain_voltage = [0,1,2,3,4,5,6,7,8,9,10]

        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            print(filename)
            with open(file_path, "r", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                
                for row in reader:
                    time.append(float(row[0]))
                    left_speed.append(float(row[1]))
                    right_speed.append(abs(float(row[2])))
        

        plt.plot(time, left_speed)
        plt.plot(time, right_speed)

    plt.show()







if __name__ == "__main__":
    main()


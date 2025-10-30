import csv
import os
import matplotlib.pylab as plt
import math
import numpy as np

def main():
    folder_path = os.path.join("Lab_0x03", "data")
    plt.figure()
    # Loop through each CSV file in the folder
    for filename in sorted(os.listdir(folder_path)):
        left_speed = []
        right_speed = []
        left_poistion = []
        right_poistion = []
        time  = []

        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            print(filename)
            with open(file_path, "r", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                
                for row in reader:
                    time.append(float(row[0]))
                    left_speed.append(float(row[3]))
                    right_speed.append(float(row[4]))
                    left_poistion.append(float(row[1]))
                    right_poistion.append(float(row[2]))
        
        #plt.plot(time, right_speed, label = f"{file_path}")
        plt.plot(time, left_speed, label = f"{file_path}")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()


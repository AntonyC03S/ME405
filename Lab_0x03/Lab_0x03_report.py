import csv
import os
import matplotlib.pylab as plt
import math
import numpy as np

def main():
    folder_path = os.path.join("Lab_0x03", "data_5")
    # fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
    # plt.subplots_adjust(right=0.78)  
    plt.figure()
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
        
        File_name = filename.split(".csv")
        plt.plot(time, right_speed, label = f"{File_name[0]} Right")
        plt.plot(time, left_speed, label = f"{File_name[0]} Left")

    plt.xlim(0,5)
    plt.title("PID Tuning Both side", fontsize = 30)
    plt.xlabel("Time, t[s]")
    plt.ylabel("Velocity, Ω[rad/s]")
    plt.legend(["P2_I19_D0.1 Right","P2.5_I20_D0.1 Left","P2_I19_D0.1 Right","P2.7_I20_D0.1 Left"])
    plt.show

    
    #     axes[0].plot(time, right_speed, label = f"{File_name[0]}")
    #     axes[1].plot(time, left_speed)
    # fig.legend(loc='center left', bbox_to_anchor=(0.82, 0.5), title="Legend",edgecolor='black')
    # fig.suptitle("PID Testing", fontsize = 30)
    # axes[0].set_xlim(0,10)
    # axes[0].set_title("Right Motor")
    # axes[1].set_title("Left Motor")
    # axes[0].set_ylabel("Velocity, Ω[rad/s]")
    # axes[1].set_xlabel("Time, t[s]") 
    # axes[1].set_ylabel("Velocity, Ω[rad/s]")
    plt.show()

if __name__ == "__main__":
    main()


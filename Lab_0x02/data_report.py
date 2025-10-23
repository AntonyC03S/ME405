import csv
import os
import matplotlib.pylab as plt
import math
import numpy as np

def main():
    folder_path = os.path.join("Lab_0x02", "data")
    fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
    plt.subplots_adjust(right=0.78)  
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
                    left_speed.append(2*math.pi*(float(row[1])/1437.1112))
                    right_speed.append(2*math.pi*(float(row[2])/1437.1112))
                    left_poistion.append(float(row[3])*4)
                    right_poistion.append(float(row[4])*4)
        

        axes[0].plot(time, right_speed)
        axes[1].plot(time, right_poistion)
        motor_gain_speed.append(right_speed[-1])



    axes[0].set_title("Step Response Comparison (Motor Position)")
    axes[1].set_title("Step Response Comparison (Motor Velocity)")
    handles = [r'$v_{m}$ = 0.00V (0% effort)',
                r'$v_{m}$ = 0.72V (10% effort)',
                r'$v_{m}$ = 1.44V (20% effort)',
                r'$v_{m}$ = 2.16V (30% effort)',
                r'$v_{m}$ = 2.88V (40% effort)',
                r'$v_{m}$ = 3.60V (50% effort)',
                r'$v_{m}$ = 4.32V (60% effort)',
                r'$v_{m}$ = 5.04V (70% effort)',
                r'$v_{m}$ = 5.76V (80% effort)',
                r'$v_{m}$ = 6.480V (90% effort)',
                r'$v_{m}$ = 7.20V (100% effort)']

    fig.legend(handles, loc='center left', bbox_to_anchor=(0.82, 0.5), title="Legend")
    
    axes[0].set_xlim(0,0.25)
    axes[0].set_ylim(0,6)
    axes[0].set_ylabel("Position, θ[rad]")
    axes[1].set_xlim(0,0.25)
    #axes[1].set_ylim(0,8)
    axes[1].set_xlabel("Time, t[s]") 
    axes[1].set_ylabel("Velocity, Ω[rad/s]")
    plt.show()

    plt.figure("MotorGain")

    x = np.array(motor_gain_voltage)
    y = np.array(motor_gain_speed)
    m, b = np.polyfit(x[1:6], y[1:6], 1)
    plt.plot(x, m*x + b, color='black', label=f'Best Fit Line: y={m:.2f}x+{b:.2f}' )

    plt.scatter(motor_gain_voltage[0:8],motor_gain_speed[0:8], label='Collect Step Response Data')
    plt.legend()
    plt.xlim(0,6.5)
    plt.ylabel("Steady State Velocity, Ω[rad/s]")
    plt.xlabel("Input Voltage $V_{m}$ [V]")
    plt.title("Motor Gain Determination")
    plt.show()
    




if __name__ == "__main__":
    main()


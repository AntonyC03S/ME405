import matplotlib.pylab as plt
import math
import numpy as np

def Extract_Data_CSV(file = "data.csv"):
    x_values = []
    trial1 = []
    trial2 = []
    trial3 = []
    trial4 = []
    trial5 = []
    trial6 = []
    trial7 = []

    with open(file, 'r') as file:
        # First line is always the column labels
        title = file.readline()

        for row, line in enumerate(file):
            try:
                # No data Error
                if line == '\n':
                    print(f"Line {row+2}: No Data. ")
                    raise
                
                # Comment Data Error
                if line[0] == "#":
                    print(f"Line {row+2}: No Data. Only Comment.")
                    raise

                # Word Data Error
                float(line[0])
                
                # Line gets split to each column data 
                lineparts = line.split(",")
                x_values.append(float(lineparts[0]))
                trial1.append(float(lineparts[1]))
                trial2.append(float(lineparts[2]))
                trial3.append(float(lineparts[3]))
                trial4.append(float(lineparts[4]))
                trial5.append(float(lineparts[5]))
                trial6.append(float(lineparts[6]))
                trial7.append(float(lineparts[7]))
            # Word Data Error
            except ValueError:
                print(f"Line {row+2}: Data is not numbers.")

            # All the other Errors
            except:
                continue
    return x_values, trial1, trial2, trial3, trial4, trial5, trial6, trial7, title


def main():  
    V_in = 3770    # mV
    R = 34190      # Ω
    C = 0.00000428 # F
    limit = 200

    # Voltage vs Time
    time, trial1, trial2, trial3, trial4, trial5, trial6, trial7, title = Extract_Data_CSV("Lab 0x00.csv")  
    time = [i/600 for i in time]
    time_experimental = time *7
    time_theoretical = time
    voltage_theoretical = [0]*100+[ V_in*(1-math.exp(-t/(R*C))) for t in time_theoretical]
    all_trails = trial1 + trial2 + trial3 + trial4 + trial5 + trial6+ trial7
    plt.rcParams.update({'font.size': 20})
    plt.figure()
    plt.plot(time_theoretical, voltage_theoretical[0:1000], color="#c44800", linewidth=3)
    plt.scatter(time_experimental, all_trails, marker='o', color="black", s=5)
    plt.title("Voltage (mV) vs Time (s)")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (mV)")
    plt.xlim(0,1.666)
    plt.ylim(0,4000)
    plt.legend(['Experimental', 'Theoretical'])
    plt.show()


    # LIN. Voltage vs Time
    plt.figure()
    time_experimental = time[0:limit] * 7
    time_theoretical = time[0:limit]
    all_trails = trial1[100:100+limit] + trial2[100:100+limit] + trial3[100:100+limit] + trial4[100:100+limit] + trial5[100:100+limit] + trial6[100:100+limit] + trial7[100:100+limit]
    y = [math.log(1-(Vout)/(V_in)) for Vout in all_trails]
    y_theoretical = [ (-t/(R*C)) for t in time_theoretical]

    plt.scatter(time_experimental, y, marker='o', color='black', s=5)
    plt.plot(time_theoretical, y_theoretical, color='#c44800')
    plt.xlim(0,0.333)
    plt.ylim(-2.25,0)
    plt.title("LIN. Voltage vs Time (s)")
    plt.xlabel("Time (s)")
    plt.ylabel("LIN. Voltage")

    # Setting intercept to 0 and getting the slope 
    A = np.array(time_experimental).reshape(-1, 1)
    m = np.linalg.lstsq(A, y, rcond=None)[0][0]
    time_curve_fit = time[0:limit]
    y_curve_fit = [ (m)*t for t in time_curve_fit]
    plt.plot(time_curve_fit, y_curve_fit, color="#5B9FF7",linestyle="--", label="Dashed (--)", linewidth=2)
    plt.legend(['Experimental', 'Theoretical', 'Experimental Curve Fit'])
    plt.text(0.275, -1.5, 'y ='+ str(round(m, 4)) +' t' , fontsize=20, color="black")
    plt.show()


if __name__ == "__main__":
    main()
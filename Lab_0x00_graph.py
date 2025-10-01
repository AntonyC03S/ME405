import matplotlib.pylab as plt
import math

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
        title = file.readline()
        for line in file:
            try:
                float(line[0])
                lineparts = line.split(",")
                x_values.append(float(lineparts[0]))
                trial1.append(float(lineparts[1]))
                trial2.append(float(lineparts[2]))
                trial3.append(float(lineparts[3]))
                trial4.append(float(lineparts[4]))
                trial5.append(float(lineparts[5]))
                trial6.append(float(lineparts[6]))
                trial7.append(float(lineparts[7]))
            except:
                continue
    return x_values, trial1, trial2, trial3, trial4, trial5, trial6, trial7, title




def main():  
    time, trial1, trial2, trial3, trial4, trial5, trial6, trial7, title = Extract_Data_CSV("Lab 0x00.csv")  
    time = [i/600 for i in time]
    plt.figure()
    plt.plot(time, trial1)
    plt.plot(time, trial2)
    plt.plot(time, trial3)
    plt.plot(time, trial4)
    plt.plot(time, trial5)
    plt.plot(time, trial6)
    plt.plot(time, trial7)
    plt.title("Voltage (mV) vs Time (s)")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (mV)")
    plt.show()


    plt.figure()
    V_in = 3770
    R = 30000
    C = 0.000001


    y_1 = [math.log(1-(Vout)/(V_in)) for Vout in trial1]
    y_2 = [math.log(1-(Vout)/(V_in)) for Vout in trial2]
    y_3 = [math.log(1-(Vout)/(V_in)) for Vout in trial3]
    x = [-t/(R*C) for t in time]
    plt.scatter(x, y_1, marker='o', color='red', s=5)
    plt.scatter(x, y_2, marker='o', color='blue', s=5)
    plt.scatter(x, y_3, marker='o', color='green', s=5)    
    plt.show()


if __name__ == "__main__":
    main()
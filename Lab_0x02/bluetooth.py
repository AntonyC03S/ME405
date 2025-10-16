from serial import Serial 

from time import sleep 

from matplotlib import pyplot 

 

times = [] 

data = [] 

 

with Serial("COM36", baudrate=115_200, timeout=1) as ser: 

    print("Opening serial port") 

    sleep(0.5) 

     

    print("Flushing serial port") 

    while ser.in_waiting: 

        ser.read() 

 

    print("Sending command to start data collection") 

    ser.write("c\r\n".encode()) 

 

    print("Waiting for data") 

    while not ser.in_waiting: continue 

 

    thead, dhead = ser.readline().decode().strip().split(",") 

    for line in ser: 

        t,d = map(float, line.decode().strip().split(",")) 

        times.append(t) 

        data.append(d) 

 

 

pyplot.plot(times,data) 

pyplot.xlabel(thead) 

pyplot.ylabel(dhead) 

pyplot.savefig("plot.svg") 


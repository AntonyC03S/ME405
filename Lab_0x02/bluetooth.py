from serial import Serial 
from time import sleep 
from matplotlib import pyplot
import csv 

 

time = [] 
left_position = []
right_position = []
left_speed = []
right_speed = []
volt = []
csv_list = []
 

with Serial("COM7", baudrate=115_200, timeout=1) as ser: 

    print("Opening serial port") 

    sleep(0.5) 

    
    print("Flushing serial port") 

    while ser.in_waiting: 

        ser.read() 

 

    print("Sending command to start data collection") 

    ser.write("c\r\n".encode()) 

 

    print("Waiting for data") 

    while not ser.in_waiting: 
        continue 

    for raw_line in ser:
        try:
            line = raw_line.decode(errors="ignore").strip()
            if not line or line == "END":
                # skip empty or end marker lines
                continue

            parts = line.split(",")
            if len(parts) != 6:
                # skip malformed lines
                print("Skipping bad line:", repr(line))
                continue

            t, lp, rp, ls, rs, v = map(float, parts)

            row_list = [t, lp, rp, ls, rs]
            csv_list.append(row_list)


            time.append(t)
            left_position.append(lp)
            right_position.append(rp)
            left_speed.append(ls)
            right_speed.append(rs)
            volt.append(v)

        except ValueError as e:
            print("ValueError on line:", repr(raw_line), "->", e)
            continue
        except Exception as e:
            print("General error:", e)
            continue 

print(f'time:{time}')
print(f'left postion: {left_position}')
print(f'right position: {right_position}')
print(f'left speed: {left_speed}')
print(f'right speed: {right_speed}')
print(f'voltage: {volt}')



with open(f"Voltage_{volt[-1]}.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(csv_list)


 

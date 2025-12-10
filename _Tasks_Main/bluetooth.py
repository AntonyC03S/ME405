from serial import Serial 
from time import sleep 
from matplotlib import pyplot
import csv 
import os
 

time = [] 
left_position = []
right_position = []
left_speed = []
right_speed = []
volt = []
csv_list = []
def unique_path(path: str) -> str:
    base, ext = os.path.splitext(path)
    i = 1
    new_path = path

    while os.path.exists(new_path):
        new_path = f"{base}_{i}{ext}"
        i += 1

    return new_path

with Serial("COM7", baudrate=115_200, timeout=1) as ser: 
# with Serial("/dev/cu.mecha12", baudrate=115_200, timeout=1) as ser: 
    print("Opening serial port") 
    sleep(0.5) 
    print("Flushing serial port") 
    while ser.in_waiting: 
        ser.read() 
    print("Sending command to start data collection") 
    # input_PID_left_gain = input("Input PID gain for left: ")
    # input_PID_right_gain = input("Input PID gain for left: ")
    
    ser.write(f"1\r\n".encode())
    print("Waiting for data") 


    time = [] 
    left_position = []
    right_position = []
    left_speed = []
    right_speed = []
    volt = []
    csv_list = []


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
            t, ls, rs, lp, rp, v = map(float, parts)
            row_list = [t, lp, rp, ls, rs]
            csv_list.append(row_list)


            time.append(t)
            left_position.append(lp)
            right_position.append(rp)
            left_speed.append(ls)
            right_speed.append(rs)

        except ValueError as e:
            print("ValueError on line:", repr(raw_line), "->", e)
            continue
        except Exception as e:
            print("General error:", e)
            continue 

    save_location = os.path.join("Lab_0x03", "data")
    save_location = os.path.join(save_location, f"Trail.csv")
    save_location = unique_path(save_location)    

    with open(save_location, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)

print(f'time:{time}')
print(f'left postion: {left_position}')
print(f'right position: {right_position}')
print(f'left speed: {left_speed}')
print(f'right speed: {right_speed}')


import csv
import os
import matplotlib.pylab as plt

def main():
    folder_path = save_location = os.path.join("Lab_0x02", "data")



    fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
    plt.subplots_adjust(right=0.78)  


    # Loop through each CSV file in the folder
    for filename in os.listdir(folder_path):
        left_speed = []
        right_speed = []
        left_poistion = []
        right_poistion = []
        voltage  = []
        time  = []
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, "r", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                header = next(reader)  # skip header or store it if needed
                
                print(f"--- {filename} ---")
                for row in reader:
                    time.append(float(row[0]))
                    left_speed.append(float(row[1]))
                    right_speed.append(float(row[2]))
                    left_poistion.append(float(row[3]))
                    right_poistion.append(float(row[4]))
                    # voltage.append(float(row[5]))
        


        # Top subplot
        axes[0].plot(time, left_speed)

        # Bottom subplot
        axes[1].plot(time, left_poistion)


    axes[0].set_title("Top Plot")
    axes[1].set_title("Bottom Plot")
    handles = [r'$v_{m}$ = 0.00V (0% effort)',
                r'$v_{m}$ = 0.72V (10% effort)',
                r'$v_{m}$ = 1.44V (20% effort)',
                r'$v_{m}$ = 2.16V (30% effort)',
                r'$v_{m}$ = 2.88V (40% effort)',
                r'$v_{m}$ = 3.60V (50% effort)',
                r'$v_{m}$ = 4.32V (60% effort)',
                r'$v_{m}$ = 5.04V (70% effort)',
                r'$v_{m}$ = 5.76V (80% effort)',
                r'$v_{m}$ = 6.480V (0% effort)',
                r'$v_{m}$ = 7.20V (100% effort)']

    # Shared legend outside (to the right)
    fig.legend(handles, loc='center left', bbox_to_anchor=(0.82, 0.5), title="Legend")

    plt.show()


if __name__ == "__main__":
    main()


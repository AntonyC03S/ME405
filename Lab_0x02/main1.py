from UI_task import UI_task
from motor_task import motor_task
from encoder_task import encoder_task
from data_task import data_task
import gc
import pyb             # type: ignore
import cotask          # type: ignore 
import task_share      # type: ignore



def main():
    print("Lab 0X02")

    # Create a share and a queue to test function and diagnostic printouts
    motor_volt           = task_share.Share('H', thread_protect=False, name="Motor Voltage Queue")
    motor_speed_left     = task_share.Queue('f', 100, thread_protect=False, overwrite=False, name="Left Motor Speed Queue")
    motor_speed_right    = task_share.Queue('f', 100, thread_protect=False, overwrite=False, name="Right Motor Speed Queue")
    motor_position_left  = task_share.Queue('f', 100, thread_protect=False, overwrite=False, name="Left Motor Position Queue")
    motor_position_right = task_share.Queue('f', 100, thread_protect=False, overwrite=False, name="Right Motor Position Queue")
    motor_time           = task_share.Queue('L', 100, thread_protect=False, overwrite=False, name="Motor Time Queue")
    motor_eff            = task_share.Share('B', thread_protect=False, name="Motor Effort Share")
    encoder_start        = task_share.Share('B', thread_protect=False, name="Encoder Start Share")
    results              = task_share.Share('L', thread_protect=False, name="Result Share")
    done                 = task_share.Share('B', thread_protect=False, name="Task Done Share")


    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(UI_task,      name="UI Task",       priority=0, period=200, profile=True, trace=False, shares=(motor_eff, results, done, motor_speed_left, motor_speed_right, motor_time, encoder_start))
    task2 = cotask.Task(motor_task,   name="Motor Task",   priority=1, period=20,  profile=True, trace=False, shares=(motor_eff, encoder_start, motor_volt, done))
    task3 = cotask.Task(encoder_task, name="Encoder Task", priority=3, period=10, profile=True, trace=False, shares=(encoder_start, motor_speed_left, motor_speed_right, motor_position_left, motor_position_right, motor_time, done))
    task4 = cotask.Task(data_task, name="Data Task", priority=2, period=10, profile=True, trace=False, shares=(motor_volt, motor_speed_left, motor_speed_right, motor_position_left, motor_position_right, motor_time, results, done))
    
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)  



    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
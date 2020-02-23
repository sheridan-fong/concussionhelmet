from sensor_library import Orientation_Sensor
from time import sleep
from gpiozero import Button, Buzzer, RGBLED
from math import pi

'''
IBEHS 1P10
Team 2 DP3 Python Program (FINAL version)
Objective: Concussion Detection
Created by: Adam Mak, Sheridan Fong
Date: 13 Feb. 2020
'''

# initialize classes
sensor = Orientation_Sensor()
status = RGBLED(10, 9, 11) # parameters represent gpio pins (r, g, b)
buzzer = Buzzer(17)
switch = Button(14)

TIME_INT = 0.01 # time delay

def average_value(values):
    try:
        avg = sum(values) / len(values)
        return avg

    except ZeroDivisionError:
        return 0

def check_concussion(radial_accel, linear_accel, conc):
    # Place holder values (matched proportions). Researched concussion thresholds have:
    # Radial acceleration > 6432 rad/s^2 (1023 rev/s^2)
    # Linear acceleration > 96.1g

    RAD_CONC_THRES = 33.3
    LIN_CONC_THRES = 30.0
    if not conc:
        if (radial_accel > RAD_CONC_THRES) or (linear_accel > LIN_CONC_THRES):
            return True

# status function
def check_status(on):
    # can be interpreted as activating status (LED) if program is running
    return True if on else status.off()

# escalation function
def file_write(radial_accel, linear_accel, conc, reset=False):
    FILENAME = 'concussion_notification.txt'
    file = open(FILENAME, 'a')

    # round if not None type
    if radial_accel:
        radial_accel = round(radial_accel, 2)
    if linear_accel:
        linear_accel = round(linear_accel, 2)
    
    file.write(str(radial_accel) + '\t' + str(linear_accel) + '\n')

    if conc:
        file.write("\nConcussed\n\n")

    if reset:
        # erases previous contents in file
        open(FILENAME, 'w').close()
        # headers
        file.write("Radial\tLinear\n")
        file.write("".center(15, "-") + "\n")
        
    file.close()
    return True

# on/off
def switch_toggle():
    if switch.is_pressed:
        buzzer.off()
        
        # off -> on
        if status.color == (0, 0, 0):
            status.color = (0, 1, 0)
            # prevent button being pressed too fast
            sleep(1)
            return True
        # on -> off
        else:
            status.color = (0, 0, 0)
            sleep(1)

def lin_accel():
    try:
        linear_accel = sensor.lin_acceleration()
    # rare error that is located outside of code (only way to fix is to catch error)
    except IOError:
        print("Fatal error, check connection!!")

    else:
        # if not None type return the max value between x, y, z
        if linear_accel[0]:
            return abs(max(linear_accel))

# notification function
def notification(radial_accel, linear_accel):
    status.color = (1, 0, 0)
    buzzer.on()
    # delays code by small amount of time to allow buzzer to noticeably go off
    print("")
    file_write(radial_accel, linear_accel, True)

# calculation function (free choice)
def rad_accel(radx_list, rady_list, radz_list):

    try:
        gyro = sensor.gyroscope() # deg/s
    except IOError:
        print("Fatal error, check connection!!")

    else:
        if gyro[0]:
            # takes x, y, z radial acceleration values
            radx_list.append(gyro[0] * pi / 180.0) # rad/s
            rady_list.append(gyro[1] * pi / 180.0)
            radz_list.append(gyro[2] * pi / 180.0)

            if len(radx_list) > 2:
                radx_list.pop(0)
                rady_list.pop(0)
                radz_list.pop(0)
            
                radx_accel = abs((radx_list[1] - radx_list[0]) / TIME_INT) # rad/s^2
                rady_accel = abs((rady_list[1] - rady_list[0]) / TIME_INT)
                radz_accel = abs((radz_list[1] - radz_list[0]) / TIME_INT)
                # only consider max value between x, y, z
                return max(radx_accel, rady_accel, radz_accel)                               

def main():
    timer = 0
    
    rad_recent_values = []
    lin_recent_values = []
    # if true, don't check for concussion
    concussed = False
    # change led color to green (signal that program is running)
    status.color = (0, 1, 0)

    # lists for managing x, y, z values
    radx_list = []
    rady_list = []
    radz_list = []

    # erases file, adds headers
    file_write("", "", False, True)
    # headers
    print("Power\t\tStatus\t\tAvg Radial\tAvg Linear\tWriting to File?")
    print("".center(80, "-"))
    
    while True:
        radial_accel = rad_accel(radx_list, rady_list, radz_list)
        linear_accel = lin_accel()
        
        on = file_write(radial_accel, linear_accel, False)

        # equivalent to avg_sensor_value
        avg_linear_accel = average_value(lin_recent_values)
        avg_radial_accel = average_value(rad_recent_values)
        
        # check if values are not None type
        if radial_accel and linear_accel:
            rad_recent_values.append(radial_accel)
            lin_recent_values.append(linear_accel)

            # checks if concussion has not occured
            if check_concussion(avg_radial_accel, avg_linear_accel, concussed):
                concussed = True
                notification(avg_radial_accel, avg_linear_accel) 

        # keeps length of recent values at 10 (most recent)
        if len(rad_recent_values) > 10:
            rad_recent_values.pop(0)
        if len(lin_recent_values) > 10:
            lin_recent_values.pop(0)

        # displays average every 1 second
        if round(timer, 2) % 1.0 == 0.0:

            if status.is_lit:
                print("ON", end='\t\t')
                if concussed:
                    print("Concussed", end='\t')
                else:
                    print("OK", end='\t\t')

                print(round(avg_radial_accel, 2), end='\t\t')
                print(round(avg_linear_accel, 2), end='\t\t')
                print("YES") if check_status(on) else print("NO")

            else:
                print("OFF", "OFF", "N/A", "N/A", "NO", sep='\t\t')
           
        # checks for concussion if button is pressed to 'on'
        if switch_toggle():
            concussed = False

        # radial acceleration relies on controlled time intervals to calculate slope
        timer += TIME_INT
        sleep(TIME_INT)
        buzzer.off() # FOR SANITY (not supposed to be here)

# for testing
def reset():
    status.off()
    buzzer.off()

main()                                                                                                                                                                                                            
#reset()

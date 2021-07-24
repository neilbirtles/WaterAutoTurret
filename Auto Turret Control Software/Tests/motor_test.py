from yaw_motor import yaw_motor as yaw_motor_class
from pitch_motor import pitch_motor as pitch_motor_class
#from GPIO import wiringPiClass
import spidev as spidev
import wiringpi
from time import sleep
import sys

OUTPUT = 1
OUTPUT_LOW = 0
OUTPUT_HIGH = 1

spi_interface = spidev.SpiDev()
spi_interface.open(1, 0)
spi_interface.max_speed_hz = 500000
spi_interface.bits_per_word = 8
spi_interface.loop = False
spi_interface.mode = 3

#setup GPIO
wiringpi.wiringPiSetup()
GPIO = wiringpi.GPIO()

#setup the yaw (rotation) motor
yaw_motor = yaw_motor_class(spi_interface, GPIO)
#setup the pitch (elvation) motor
pitch_motor = pitch_motor_class(spi_interface, GPIO)

def print_debug_info():
    print("Yaw Driver Status: " + str(bin(yaw_motor.DRV_STATUS)))
    print("Yaw Latest SPI Info: " + str(bin(yaw_motor.current_SPI_status)))
    print("Pitch Driver Status: " + str(bin(pitch_motor.DRV_STATUS)))
    print("Pitch Latest SPI Info: " + str(bin(pitch_motor.current_SPI_status)))
    print("Yaw TSTEP: " + str(yaw_motor.TSTEP))
    print("Pitch TSTEP: " + str(pitch_motor.TSTEP))

error = False

while True:
    new_input = input("p x pitch motor target pos, y x yaw motor target pos, z set zero, h home, a automove, d debug info, r reset, s get RAMPSTAT 10 times, q to exit: ")
    if new_input == "d":
        print_debug_info()
        new_input = str(yaw_motor.current_position)

    if new_input == "r":
        yaw_motor.CHOPCONF = 0x4000000
        sleep(0.1)
        yaw_motor.CHOPCONF = 0x4000005
        yaw_motor.GSTAT = 0x03

        pitch_motor.CHOPCONF = 0x4000000
        sleep(0.1)
        pitch_motor.CHOPCONF = 0x4000005
        pitch_motor.GSTAT = 0x03
        new_input = str(yaw_motor.current_position)
    
    if new_input =="h":
        print("Homing Yaw Motor...")
        yaw_motor.home(1000, 51200, 10)
        print("Yaw Homed")
        print("----------------------")
        new_input = str(yaw_motor.current_position)
        print("Homing Pitch Motor...")
        pitch_motor.home(500, 51200, 10)
        print("Pitch Homed")
        print("----------------------")

    if new_input == "s":
        counter = 0
        while counter < 50:
            print ("yaw motor RAMPSTAT: " + bin(yaw_motor.RAMPSTAT))
            print ("pitch motor RAMPSTAT: " + bin(pitch_motor.RAMPSTAT))
            sleep(1)
            counter= counter+1
        new_input = str(yaw_motor.current_position)

    if new_input == "q":
        #take the pitch motor down to its limit so the barrel doesnt flop down!
        pitch_motor.go_to_position(pitch_motor.max_left_steps)
        break
    
    if new_input == "z":
        yaw_motor.XACTUAL = 0
        pitch_motor.XACTUAL = 0
        new_input = "0"

    if new_input == "a":
        if yaw_motor.homed & pitch_motor.homed:
            pitch_dir = 0
            yaw_dir = 0
            move_count = 0
            yaw_motor.go_to_position(yaw_motor.max_left_steps)
            pitch_motor.go_to_position(pitch_motor.max_left_steps)

            while move_count < 5:
                if yaw_motor.position_reached:
                    if yaw_dir == 0:
                        yaw_dir = 1
                        yaw_motor.go_to_position(yaw_motor.max_right_steps)
                        print("Y0")
                        move_count = move_count + 1
                    else:
                        yaw_dir = 0
                        yaw_motor.go_to_position(yaw_motor.max_left_steps)
                        print("Y1")
                        move_count = move_count + 1

                if pitch_motor.position_reached:
                    if pitch_dir == 0:
                        pitch_dir = 1
                        pitch_motor.go_to_position(pitch_motor.max_right_steps)
                        print("P0")
                    else:
                        pitch_dir = 0
                        pitch_motor.go_to_position(pitch_motor.max_left_steps)
                        print("P1")
                sleep(0.1)
            
            #take both motors back home at end
            yaw_motor.go_to_position(0)
            pitch_motor.go_to_position(0)
        else:
            print("Home motors before automove")
    
    if "y" in new_input:
        if yaw_motor.homed:
            try:
                requested_position = int(new_input.split()[1])
                if requested_position < yaw_motor.max_left_steps or requested_position > yaw_motor.max_right_steps:
                    print("Requested move outside target range, max is " + str(yaw_motor.max_left_steps) + " to " + str(yaw_motor.max_right_steps))
                else:
                    print("going to target: " + str(requested_position))
                    yaw_motor.go_to_position(requested_position)
                    print(yaw_motor.position_reached)
                    
                    while not yaw_motor.position_reached:
                        print("moving...")
                        print ("A: "+ str(yaw_motor.XACTUAL))
                        print ("T: "+ str(yaw_motor.XTARGET))
                        sleep(0.5)
            except:
                print("Invalid position entered")
        else:
            print("Home motors before move")
    
    if "p" in new_input:
        if pitch_motor.homed:
            try:
                requested_position = int(new_input.split()[1])
                if requested_position < pitch_motor.max_left_steps or requested_position > pitch_motor.max_right_steps:
                    print("Requested move outside target range, max is " + str(pitch_motor.max_left_steps) + " to " + str(pitch_motor.max_right_steps))
                else:
                    print("going to target: " + str(requested_position))
                    pitch_motor.go_to_position(requested_position)
                    print(pitch_motor.position_reached)
                    
                    while not pitch_motor.position_reached:
                        print("moving...")
                        print ("A: "+ str(pitch_motor.XACTUAL))
                        print ("T: "+ str(pitch_motor.XTARGET))
                        sleep(0.5)
            except:
                print("Invalid position entered")
        else:
            print("Home motors before move")
    
    error=False

print("quitting")
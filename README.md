# Water Auto Turret

This is a fully automatic water turret that will track people and fire water at them. Intended to be a toy for children in the summer! Its constructed from a mix of 3D printed parts, aluminium extrusions and various other off the shelf items. The unit is powered by a 12v lead acid battery and plugs into a standard hosepipe push on connector for its water supply. It uses a Khadas VIM3 board to control everything and uses the onboard NPU to do the object tracking.

Full design information will be published here for those that want to make one for themselves

Current stage of development is:
    Mechanics: 90% complete, all functional items are working, just a few covers and minor parts need to be constructed
    Electronics: 95% complete, there are a couple of errors that need to be fixed in the rev2 PCB, but otherwise working
    Software: 50% complete, drivers and test code complete for the water control solenoids and stepper motors and an interface to YOLOv3 is implemented along with initial web front end


## Mechanics

All mechanical items have been designed in Fusion360 - model files to be published. 3D printed items have been printed on a Prusa Mk3S+

## Electronics

Main controller board is a Khadas VIM3. A custom PCB is used to interface to the Water Auto Turret. The PCB mounts a DRV8806 chip for driving 4 solenoids for controlling water flow to the turret, two Trinamic TMC5160 breakout boards for controlling the pitch and yaw stepper motors and some battery monitoring / power control circuitry

## Software 

Interface between the control electronics and the Khadas VIM3 is via WiringPi and SPI dev coded in python so should allow for porting to other SBC such as Raspberry Pi, but there will be obvious limitations for the object tracking if a board without an NPU is used. 

TMC5160_driver.py       - provides a generic TMC5160 driver written in python using WiringPi and SPIdev 
motor_test.py           - exercises the TMC5160 driver and allows both motors to be homed and then manually and automatically moved 

DRV8806_driver.py       - provides a driver for the DRV8806 chip written in python using WiringPi
solenoids_test.py       - exercises the DRV8806 driver and does a simple sequence of closing and opening the 4 valves 

KhadasYolov3Detector    - uses the Khadas Yolo v3 demo from here https://gitlab.com/khadas/aml_npu_app and adds in a simple TCP server to output the detections in JSON format to allow them to be used by the main python application 

Webserver               - initial outline of a flask web front end to provide control info for the water auto turret 
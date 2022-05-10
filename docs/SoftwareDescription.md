# Software Description
The software for the Water Auto Turret has been implemented in four main parts:
* A Web Application using the Flask framework to provide the user interface
* The Khadas Software Neural Network (Python API) to carry out the computer vision to identify potential targets
* A turret controller that takes the potential targets and converts this to turret movement information and feeds this information back to the web front end
* Low level drivers to control the motors, solenoids etc.

The code has been pretty thoroughly commented so should be relatively self explanatory however and overview is given below. I am not a software developer and have self taught myself python so welcome any feedback on improvements and or better ways of implementing this code!

### Web Application
This is a standard Flask web application that is started using the command `python3 autoturret.py`

Within the [\_\_init__.py](https://github.com/neilbirtles/WaterAutoTurret/blob/main/Auto%20Turret%20Control%20Software/autoturretwebapp/__init__.py) file the following are initialised:
* motors - provides setup of the SPI / GPIO interfaces, initialisation (inc chip select pin definition) and carries out the homing for the  pitch_motor and yaw_motors. Both motors use the lower level TMC5160_driver for interfacing to the TMC5160 Breakout Boards.
* solenoids - provides setup and initialisation of the solenoid interface including the GPIO pins used for the interface to the lower level DRV8806 driver.
* detection_model_params - provides and initial setup of parameters for the detection model. Created to provide easier change in the future
* turret_controller - the turret controller which is where all the neural network processing is carried out. This is spawned in a separate thread to prevent the web app becoming blocked. Outputs from this thread are loaded into a standard Python Queue to allow the outputs to be grabbed by the web app to display on the front end.
* app_thread_pool - provides the thread pool (that the turret_controller is spawned in), events for notifications into/out of the thread and also the pipeline for exchanging information out of the thread

After this initialisation the Flask app is started and the system is ready for targets!

In the routes.py file the generate() function attempts to grabs video frames from the Queue and allows them to be displayed on the web front end. The rate this grab happens is adjusted to slightly faster than the current frame rate to get a decent refresh rate on the screen without this function looping instantly and using all processing power (as it did when I first wrote it…)

### KSNN Yolov3
The Water Auto Turret uses the Yolo v3 model to carry out the object detection and tracking. The code for this can be found in the [turret_controller.py](https://github.com/neilbirtles/WaterAutoTurret/blob/main/Auto%20Turret%20Control%20Software/autoturretwebapp/turret_controller.py) file and draws on the Khadas examples. The Yolo v3 model and lib files are the standard Khadas provided ones. 

The detection works as follows:
* Setup the KSNN
* Initialise the neural network with the Yolo v3 model
* Setup the opencv capture devices
* Loop around the following:
  * Grab a video frame
  * Carry out inference
  * Transform the returned data into the format required for post processing
  * Extract the bounding boxes, associated class names and probability scores from the returned data
  * Scale the grabbed frame to be the right size to display in the web front end
  * Get targets from the neural network returned data (including marking these up in the grabbed frame
  * Pass the grabbed frame into Queue to allow it to be grabbed by the web front end for display

### Turret Controller
The turret control software can also be found in the [turret_controller.py](https://github.com/neilbirtles/WaterAutoTurret/blob/main/Auto%20Turret%20Control%20Software/autoturretwebapp/turret_controller.py) file. The target detection loop through all the object detections passed out from the neural network processing and does the following checks on each to identify targets:
* Checks if the detected object is a “person” and if the probability is above the detection threshold
* If both are true then annotate the target in the image frame with “TARGET ACQUIRED”
* Calculate the mid point of the target to allow the Water Auto Turret to target it with water
* Draw a red * at the midpoint of the target in the image frame
* Scale the target image coordinates into the pitch and yaw step ranges (calculated during the initial homing procedure)
* Check if the difference in the new target coordinate is greater than the move threshold in both pitch and yaw motions
* If the difference is greater than the move threshold then move the appropriate motor(s) to the new target positions
* If there are one or more targets then turn on the water and if there arent then turn off the water (at the current time all 4 water ports are turned on or off at the same time)

### Low Level Drivers
#### TMC5160
The driver for this is provided in [TMC5160_driver.py](https://github.com/neilbirtles/WaterAutoTurret/blob/main/Auto%20Turret%20Control%20Software/autoturretwebapp/TMC5160_driver.py). The driver exposes all the functions of the TMC5160 that are currently used and have been used in development but does not provide all features of the TMC5160 device. The internal __read_from_TMC_5160 and __write_to_TMC5160 functions provide the interface direct to the chip. Other higher level functions are exposed from the driver such as “home”. The code in this file is well documented and is directly derived from the [TMC5160 datasheet](https://www.trinamic.com/fileadmin/assets/Products/ICs_Documents/TMC5160A_datasheet_rev1.16.pdf) so should be read in conjunction with the datasheet to get a full understanding of how it works.

#### DRV8806
The driver for this is provided in the [DRV8806_driver.py](https://github.com/neilbirtles/WaterAutoTurret/blob/main/Auto%20Turret%20Control%20Software/autoturretwebapp/DRV8806_driver.py). This should again be read in conjunction with the datasheet for the [DRV8806](https://www.ti.com/lit/gpn/drv8806) but this is much simpler than the TMC5160 as the interface is essentially - set or reset the data bit to indicate a solenoid driving being on or off respectively, clock this data bit into the device by strobing the clock line, repeat this 3 times more to get data bits for all 4 outputs into the device and then latch that data into the outputs. Again the code is documented so should be easy to understand. 

### Tests
In the “Tests” folder there are some standalone test files that can be used when debugging the system or for testing during assembly
* [motor_test.py](https://github.com/neilbirtles/WaterAutoTurret/blob/main/Auto%20Turret%20Control%20Software/Tests/motor_test.py) - allows for manual homing and setup whilst providing low level feedback from the driver code. The functionality for this can be seen from the code or from running the file and reading the prompts
* [solenoids_test.py](https://github.com/neilbirtles/WaterAutoTurret/blob/main/Auto%20Turret%20Control%20Software/Tests/solenoids_test.py) - provides a sequence that turns on each solenoid valve in sequence 0.5 seconds apart, waits 1 second and then turns them off in sequence 0.5 seconds apart. This produces an audible clicking that can be used to ensure all solenoids are working

## Future Software Development
The Water Auto Turret is currently fully functional, however its always possible to get better! For this reason the following areas of software are currently under development:
* Improved target tracking using OpenCV for detection at a reduced frame rate and then using the much lighter weight [Dlib for tracking](http://dlib.net/correlation_tracker.py.html) with the aim or providing more frequent updates to the targeting 
* Improved alignment between objects being tracked and targeting - at the moment this is a linear scale relationship and this doesn't work as well as it could as the target moves away from centre

[{Home}](README.md) [{Next}](3DPrintedParts.md)

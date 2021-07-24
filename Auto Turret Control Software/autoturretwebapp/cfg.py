import os
import subprocess
import socket
import sys
import json

#launch detection framework
#p = subprocess.Popen(['/home/khadas/waterautoturret/KhadasYolov3Detector/yolo_demo_x11_mipi/bin_r_cv4/detect_demo_x11_mipi', '-d /dev/video0', '-m 2'],cwd="/home/khadas/waterautoturret/KhadasYolov3Detector/yolo_demo_x11_mipi/bin_r_cv4/")
# p = subprocess.
# os.chdir("/home/khadas/waterautoturret/KhadasYolov3Detector/yolo_demo_x11_mipi/bin_r_cv4/")
# os.system("./detect_demo_x11_mipi -d /dev/video0 -m 2")


server_address = ('localhost', 4141)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

detection_image_width = 0
detection_image_height = 0
#percentage certainty before responding
detection_threshold = 85
detection_movement_yaw_threshold = int(yaw_motor.max_total_steps * 0.05)
detection_movement_pitch_threshold = int(pitch_motor.max_total_steps * 0.05)

while(0):
    try:
        #string comes from c which uses a null terminator at the end so convert to utf-8 format and strip the null
        data = sock.recv(1024).decode('utf-8', "ignore")
        received_detection = json.loads(str(data).rstrip('\x00'))
        
        #if this is the initial join message then get the detection image sizes to allow scaling for movements
        if "joinmessage" in received_detection:
            detection_image_height = int(received_detection["image_height"])
            detection_image_width = int(received_detection["image_width"])

            print(str(detection_image_height))
            print(str(detection_image_width))
        
        if "labelname" in received_detection:
            if "person" in received_detection["labelname"]:
                #got a detection containing a person 
                #{'detectid': '0', 'labelname': 'person: 55% ', 'left': '868.921387', 'right': '1588.921387', 'top': '0.000000', 'bottom': '1080.000000'}
                detection_certainty = int(str(received_detection["labelname"]).split()[1].strip('%'))
                if detection_certainty > detection_threshold:
                    print("Got a person over detection threshold of " + str(detection_threshold) + "%")
                    detection_left_right_mid_point = int(float(received_detection["right"]) - float(received_detection["left"]))
                    detection_up_down_mid_point = int(float(received_detection["bottom"]) - float(received_detection["top"]))
                    print("Detection left right mid point: " + str(detection_left_right_mid_point))
                    print("Detection up down mid point: " + str(detection_up_down_mid_point))
                    print("Yaw max: " + str(yaw_motor.max_total_steps))
                    detection_yaw_target = int((detection_left_right_mid_point / detection_image_width) * yaw_motor.max_total_steps)
                    print("Detection yaw target" + str(detection_yaw_target))
                    detection_pitch_target = int((detection_up_down_mid_point / detection_image_height) * pitch_motor.max_total_steps)
                    print("Pitch max: " + str(pitch_motor.max_total_steps))
                    print("Detection pitch target" + str(detection_pitch_target))

                    #translate to target positions and see if outside movement threshold - if they are then move to them 
                    yaw_step_target = -1 * (detection_yaw_target + yaw_motor.max_left_steps)
                    print("Current Target: " + str(yaw_motor.current_target))
                    print("New Target: " + str(yaw_step_target))
                    if yaw_step_target < yaw_motor.current_target - detection_movement_yaw_threshold or yaw_step_target > yaw_motor.current_target + detection_movement_yaw_threshold:
                        print("got a yaw move")
                        yaw_motor.go_to_position(yaw_step_target)
                    else:
                        print("yaw move under movement threshold")
    except:
        print("Error data")
        print(repr(data))
        print("-----")

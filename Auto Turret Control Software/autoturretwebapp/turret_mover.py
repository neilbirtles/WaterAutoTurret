from time import sleep

DEBUG=True

def turret_mover(queue, event, modelparams, yaw_motor, pitch_motor):

    #process movement messages until the thread is signaled to close, and even then get to the end of the movement messages first
    while not event.is_set() or not queue.empty():
        #sleep if there are no messages to process or the motors havent been homed yet
        if queue.empty() or not yaw_motor.homed or not pitch_motor.homed:
            sleep(0.001)
        else:
            received_detection = queue.get()
            if DEBUG: 
                print("Processing detection message: " + str(received_detection))
                print(str(queue.qsize) + " messages remaining in the queue")
                
                #got a detection containing a person 
                #{'detectid': '0', 'labelname': 'person: 55% ', 'left': '868.921387', 'right': '1588.921387', 'top': '0.000000', 'bottom': '1080.000000'}
                
                detection_left_right_mid_point = int(float(received_detection["right"]) - float(received_detection["left"]))
                detection_up_down_mid_point = int(float(received_detection["bottom"]) - float(received_detection["top"]))
                if DEBUG: 
                    print("Detection left right mid point: " + str(detection_left_right_mid_point))
                    print("Detection up down mid point: " + str(detection_up_down_mid_point))
                    print("Yaw max: " + str(yaw_motor.max_total_steps))
                detection_yaw_target = int((detection_left_right_mid_point / modelparams.det_img_width) * yaw_motor.max_total_steps)
                if DEBUG:
                    print("Detection yaw target" + str(detection_yaw_target))
                detection_pitch_target = int((detection_up_down_mid_point / modelparams.det_img_height) * pitch_motor.max_total_steps)
                if DEBUG:
                    print("Pitch max: " + str(pitch_motor.max_total_steps))
                    print("Detection pitch target" + str(detection_pitch_target))

                #translate to target positions and see if outside movement threshold - if they are then move to them 
                #yaw move
                yaw_step_target = -1 * (detection_yaw_target + yaw_motor.max_left_steps)
                if DEBUG:
                    print("Current Yaw Target: " + str(yaw_motor.current_target))
                    print("New Yaw Target: " + str(yaw_step_target))
                if yaw_step_target < yaw_motor.current_target - modelparams.det_move_threshold_yaw or yaw_step_target > yaw_motor.current_target + modelparams.det_move_threshold_yaw:
                    if DEBUG: print("got a yaw move")
                    yaw_motor.go_to_position(yaw_step_target)
                else:
                    if DEBUG: print("yaw move under movement threshold")
                #pitch move
                pitch_step_target = -1 * (detection_pitch_target + pitch_motor.max_left_steps)
                if DEBUG:
                    print("Current Pitch Target: " + str(pitch_motor.current_target))
                    print("New Pitch Target: " + str(pitch_step_target))
                if pitch_step_target < pitch_motor.current_target - modelparams.det_move_threshold_pitch or pitch_step_target > pitch_motor.current_target + modelparams.det_move_threshold_pitch:
                    if DEBUG: print("got a pitch move")
                    pitch_motor.go_to_position(pitch_step_target)
                else:
                    if DEBUG: print("pitch move under movement threshold")
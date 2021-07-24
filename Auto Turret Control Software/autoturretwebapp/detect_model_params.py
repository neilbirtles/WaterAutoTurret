

class detect_model_params():
    
    def __init__(self, yaw_motor_max_steps, pitch_motor_max_steps):
        self.__yaw_motor_max_steps = yaw_motor_max_steps
        self.__pitch_motor_max_steps = pitch_motor_max_steps
        # size of the detection image, used to work out translation of co-ordinates
        self.__detection_image_width = 0
        self.__detection_image_height = 0
        #percentage certainty before responding
        self.__detection_threshold = 85
        #movement in steps that has to be breached before movement occurs to take out the image jitter
        self.__detection_movement_yaw_threshold = 26
        self.__detection_movement_pitch_threshold = 4
        #movement threshold as a percentage of total steps
        self.__detection_movement_pitch_threshold_percentage = 0.05
        self.__detection_movement_yaw_threshold_percentage = 0.05

    @property
    def det_img_width(self):
        return self.__detection_image_width
    
    @det_img_width.setter
    def det_img_width(self, value):
        self.__detection_image_width = value

    @property
    def det_img_height(self):
        return self.__detection_image_height
    
    @det_img_height.setter
    def det_img_height(self, value):
        self.__detection_image_height = value

    @property
    def detection_threshold(self):
        return self.__detection_threshold
    
    @detection_threshold.setter
    def detection_threshold(self, value):
        self.__detection_threshold = value

    @property
    def det_move_threshold_yaw(self):
        return self.__detection_movement_yaw_threshold

    @property
    def det_move_threshold_pitch(self):
        return self.__detection_movement_pitch_threshold
    
    @property
    def det_move_threshold_yaw_percentage(self):
        return self.__detection_movement_yaw_threshold_percentage * 100
    
    @det_move_threshold_yaw_percentage.setter
    def det_move_threshold_yaw_percentage(self, value):
        self.__detection_movement_yaw_threshold_percentage = value / 100
        self.__detection_movement_yaw_threshold = int(self.__yaw_motor_max_steps*(self.__detection_movement_yaw_threshold_percentage))
    
    @property
    def det_move_threshold_pitch_percentage(self):
        return self.__detection_movement_pitch_threshold_percentage * 100
    
    @det_move_threshold_pitch_percentage.setter
    def det_move_threshold_pitch_percentage(self, value):
        self.__detection_movement_pitch_threshold_percentage = value / 100
        self.__detection_movement_pitch_threshold = int(self.__pitch_motor_max_steps*(self.__detection_movement_pitch_threshold_percentage))
    
    #TODO - add in calibration sizes for targets - height and width to help with range estimation
    
    


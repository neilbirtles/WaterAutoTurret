from flask import Flask
from flask_bootstrap import Bootstrap
from .motors import pitch_motor
from .motors import yaw_motor
from .solenoids import water_ports
from .detect_model_params import detect_model_params



def init_autoturret():
    app = Flask(__name__)
    app.config.from_pyfile('appconfig.cfg')

    modelparams = detect_model_params(yaw_motor.max_total_steps, pitch_motor.max_total_steps)
    #start with a 5% move threshold
    modelparams.det_move_threshold_pitch_percentage = 5
    modelparams.det_move_threshold_yaw_percentage = 5

    #setup and start the threads for the yolo model interface and the turret movement 
    ##TODO---------------------------------***************************

    with app.app_context():
        from autoturretwebapp import routes

        bootstrap = Bootstrap(app)

        return app
import threading
import atexit
from flask import Flask
from flask_bootstrap import Bootstrap
from .motors import pitch_motor
from .motors import yaw_motor
from .solenoids import water_ports
from .detect_model_params import detect_model_params
from .yolo_model_interface import yolo_model_interface
from .turret_mover import turret_mover
from .turret_controller import turret_controller
from .app_thread_pool import app_thread_pool_executor
from .app_thread_pool import event
from .app_thread_pool import pipeline

def close_down():
    event.set()
    app_thread_pool_executor.shutdown(wait=False)

def init_autoturret():
    app = Flask(__name__)
    app.config.from_pyfile('appconfig.cfg')

    modelparams = detect_model_params(yaw_motor.max_total_steps, pitch_motor.max_total_steps)
    #start with a 5% move threshold
    modelparams.det_move_threshold_pitch_percentage = 2
    modelparams.det_move_threshold_yaw_percentage = 2

    #app_thread_pool_executor.submit(yolo_model_interface, pipeline, event, modelparams, app.config['YOLO_SERVER_IP'], app.config['YOLO_SERVER_PORT'])
    #app_thread_pool_executor.submit(turret_mover, pipeline, event, modelparams, yaw_motor, pitch_motor)
    app_thread_pool_executor.submit(turret_controller, pipeline, event, modelparams, yaw_motor, pitch_motor, water_ports, app.config['NB_FILE_LOCATION'], app.config['SO_LIB_LOCATION'], app.config['VIDEO_DEVICE'], 40)
    atexit.register(close_down)


    with app.app_context():
        from autoturretwebapp import routes

        bootstrap = Bootstrap(app)

        return app

    
from time import sleep
from pathlib import Path
from flask import render_template
from flask import jsonify
from flask import request
from flask import Response
from flask import flash, url_for, redirect
from werkzeug.utils import secure_filename
from autoturretwebapp import app
from .cfg import pitch_motor
from .cfg import yaw_motor
import random
import string
import sys
import os

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    templateData = {
        'yaw_left_max' : yaw_motor.max_left_steps,
        'yaw_right_max' : yaw_motor.max_right_steps,
        'pitch_left_max' : pitch_motor.max_left_steps,
        'pitch_right_max' : pitch_motor.max_right_steps
    }
    return render_template('index.html', **templateData)

#------------------------------------------------

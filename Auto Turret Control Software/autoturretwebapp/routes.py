from time import sleep
from pathlib import Path
from flask import render_template
from flask import jsonify
from flask import request
from flask import Response
from flask import flash, url_for, redirect
from werkzeug.utils import secure_filename
from flask import current_app as app
from .motors import pitch_motor
from .motors import yaw_motor
from .app_thread_pool import pipeline
import cv2 as cv
import random
import string
import sys
import os

DEBUG = False

# Grabs frames from the pipeline and yields them 
def generate():
    sleep_time = 0.05
    while True:
        if not pipeline.empty():
            output_data = pipeline.get()
            if DEBUG: print("[Display] Got data")
            #the image frame is the first item in the list
            frame = output_data[0]
            # encode the frame in JPEG format
            if DEBUG: print("[Generate] Encoding img")
            (flag, encodedFrame) = cv.imencode(".jpg", frame)
            if DEBUG: print("[Generate] Encoding flag: " + str(flag))
            if flag:
                #yield the output from in byte format
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedFrame) + b'\r\n')
            #number of frames per second is second item in the list
            fps = output_data[1]
            if fps > 0:
                #adjust the sleep time to roughly align with the frames per second being generated for least CPU usage, but make it slightly faster
                sleep_time = 1/(fps*1.2)
                if DEBUG: print(f"[Display] FPS: {fps:.1f} and sleep time: {sleep_time:.4f}")
        sleep(sleep_time)

@app.route("/yolo_video_ouput")
def yolo_video_ouput():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

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

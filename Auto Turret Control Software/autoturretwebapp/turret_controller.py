from ctypes import *
import time
import numpy as np
from ksnn.api import KSNN
from ksnn.types import *

import cv2 as cv

DEBUG = False

GRID0 = 13
GRID1 = 26
GRID2 = 52
LISTSIZE = 85
SPAN = 3
OBJ_THRESH = 0.5
NMS_THRESH = 0.6
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

CLASSES = ("person", "bicycle", "car","motorbike ","aeroplane ","bus ","train","truck ","boat","traffic light",
           "fire hydrant","stop sign ","parking meter","bench","bird","cat","dog ","horse ","sheep","cow","elephant",
           "bear","zebra ","giraffe","backpack","umbrella","handbag","tie","suitcase","frisbee","skis","snowboard","sports ball","kite",
           "baseball bat","baseball glove","skateboard","surfboard","tennis racket","bottle","wine glass","cup","fork","knife ",
           "spoon","bowl","banana","apple","sandwich","orange","broccoli","carrot","hot dog","pizza ","donut","cake","chair","sofa",
           "pottedplant","bed","diningtable","toilet ","tvmonitor","laptop	","mouse	","remote ","keyboard ","cell phone","microwave ",
           "oven ","toaster","sink","refrigerator ","book","clock","vase","scissors ","teddy bear ","hair drier", "toothbrush ")

def sigmoid(x):
	return 1 / (1 + np.exp(-x))


def process(input, mask, anchors):

	anchors = [anchors[i] for i in mask]
	grid_h, grid_w = map(int, input.shape[0:2])

	box_confidence = sigmoid(input[..., 4])
	box_confidence = np.expand_dims(box_confidence, axis=-1)

	box_class_probs = sigmoid(input[..., 5:])

	box_xy = sigmoid(input[..., :2])
	box_wh = np.exp(input[..., 2:4])
	box_wh = box_wh * anchors

	col = np.tile(np.arange(0, grid_w), grid_w).reshape(-1, grid_w)
	row = np.tile(np.arange(0, grid_h).reshape(-1, 1), grid_h)

	col = col.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
	row = row.reshape(grid_h, grid_w, 1, 1).repeat(3, axis=-2)
	grid = np.concatenate((col, row), axis=-1)

	box_xy += grid
	box_xy /= (grid_w, grid_h)
	box_wh /= (416, 416)
	box_xy -= (box_wh / 2.)
	box = np.concatenate((box_xy, box_wh), axis=-1)

	return box, box_confidence, box_class_probs

def filter_boxes(boxes, box_confidences, box_class_probs):
	box_scores = box_confidences * box_class_probs
	box_classes = np.argmax(box_scores, axis=-1)
	box_class_scores = np.max(box_scores, axis=-1)
	pos = np.where(box_class_scores >= OBJ_THRESH)

	boxes = boxes[pos]
	classes = box_classes[pos]
	scores = box_class_scores[pos]

	return boxes, classes, scores

def nms_boxes(boxes, scores):
	x = boxes[:, 0]
	y = boxes[:, 1]
	w = boxes[:, 2]
	h = boxes[:, 3]

	areas = w * h
	order = scores.argsort()[::-1]

	keep = []
	while order.size > 0:
		i = order[0]
		keep.append(i)

		xx1 = np.maximum(x[i], x[order[1:]])
		yy1 = np.maximum(y[i], y[order[1:]])
		xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
		yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])

		w1 = np.maximum(0.0, xx2 - xx1 + 0.00001)
		h1 = np.maximum(0.0, yy2 - yy1 + 0.00001)
		inter = w1 * h1

		ovr = inter / (areas[i] + areas[order[1:]] - inter)
		inds = np.where(ovr <= NMS_THRESH)[0]
		order = order[inds + 1]
	keep = np.array(keep)
	return keep

def yolov3_post_process(input_data):
	masks = [[6, 7, 8], [3, 4, 5], [0, 1, 2]]
	anchors = [[10, 13], [16, 30], [33, 23], [30, 61], [62, 45],
			[59, 119], [116, 90], [156, 198], [373, 326]]

	boxes, classes, scores = [], [], []
	for input,mask in zip(input_data, masks):
		b, c, s = process(input, mask, anchors)
		b, c, s = filter_boxes(b, c, s)
		boxes.append(b)
		classes.append(c)
		scores.append(s)

	boxes = np.concatenate(boxes)
	classes = np.concatenate(classes)
	scores = np.concatenate(scores)

	nboxes, nclasses, nscores = [], [], []
	for c in set(classes):
		inds = np.where(classes == c)
		b = boxes[inds]
		c = classes[inds]
		s = scores[inds]

		keep = nms_boxes(b, s)

		nboxes.append(b[keep])
		nclasses.append(c[keep])
		nscores.append(s[keep])

	if not nclasses and not nscores:
		return None, None, None

	boxes = np.concatenate(nboxes)
	classes = np.concatenate(nclasses)
	scores = np.concatenate(nscores)

	return boxes, classes, scores

def draw(image, boxes, scores, classes):
	for box, score, cl in zip(boxes, scores, classes):
		x, y, w, h = box
		x *= image.shape[1]
		y *= image.shape[0]
		w *= image.shape[1]
		h *= image.shape[0]
		if DEBUG: print(f"[turret contoller] Detection Class: {CLASSES[cl]} and Score: {score:.0%}")
		if DEBUG: print(f"[turret contoller] Detection box (left,top,right,down): [{(x):.1f}, {(y):.1f}, {(x+w):.1f}, {(y+h):.1f}]")
		top = max(0, np.floor(x + 0.5).astype(int))
		left = max(0, np.floor(y + 0.5).astype(int))
		right = min(image.shape[1], np.floor(x + w + 0.5).astype(int))
		bottom = min(image.shape[0], np.floor(y + h + 0.5).astype(int))
		
		cv.rectangle(image, (top, left), (right, bottom), (0, 255, 0), 2)
		cv.putText(image, f"{CLASSES[cl]} {score:.0%}", (top, left - 6), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

def target_turret(image):
	cv.drawMarker(image, (int(image.shape[1]/2),int(image.shape[0]/2)), color=(0,0,255), markerType=cv.MARKER_STAR)

def get_targets(image, boxes, scores, classes, model_params, yaw_motor, pitch_motor, water_ports):
	got_target = False

	for box, score, cl in zip(boxes, scores, classes):
		if CLASSES[cl] == "person" and score >= model_params.detection_threshold/100:
			#got a person that is over the detection certainty threshold - so box it and target it
			got_target = True
			x, y, w, h = box
			x *= image.shape[1]
			y *= image.shape[0]
			w *= image.shape[1]
			h *= image.shape[0]
			if DEBUG: print(f"[turret contoller] Detected target with score: {score:.0%}")
			if DEBUG: print(f"[turret contoller] Detection box (left,top,right,down): [{(x):.1f}, {(y):.1f}, {(x+w):.1f}, {(y+h):.1f}]")
			top = max(0, np.floor(y + 0.5).astype(int))
			left = max(0, np.floor(x + 0.5).astype(int))
			right = min(image.shape[1], np.floor(x + w + 0.5).astype(int))
			bottom = min(image.shape[0], np.floor(y + h + 0.5).astype(int))
			#draw and label the box
			cv.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
			if DEBUG:
				cv.putText(image, f"TARGET - {score:.0%}, T:{top},L:{left},R:{right},B:{bottom}", (left, top - 6), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
			else:
				cv.putText(image, f"TARGET ACQUIRED", (left, top - 6), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
			#create target info
			detection_left_right_mid_point = int(((right - left)/2)+left)
			detection_up_down_mid_point = int(((bottom - top)/2)+top)
			#scale into max steps for the turret
			detection_yaw_target = int((detection_left_right_mid_point / image.shape[1]) * yaw_motor.max_total_steps)
			detection_pitch_target = int((detection_up_down_mid_point / image.shape[0]) * pitch_motor.max_total_steps)
			
			if DEBUG: 
				print("Detection left right mid point: " + str(detection_left_right_mid_point))
				print("Detection up down mid point: " + str(detection_up_down_mid_point))
				print("Detection yaw target: " + str(detection_yaw_target))
				print("Detection pitch target: " + str(detection_pitch_target))

			# yaw_step_target = -1 * (detection_yaw_target + yaw_motor.max_left_steps)
			pitch_step_target = -1 * (detection_pitch_target + pitch_motor.max_left_steps)
			yaw_step_target = detection_yaw_target + yaw_motor.max_left_steps
			#pitch_step_target = detection_pitch_target + pitch_motor.max_left_steps
			
			#draw the target marker and label it with target step positions
			cv.drawMarker(image, (detection_left_right_mid_point,detection_up_down_mid_point), color=(0,0,255), markerType=cv.MARKER_STAR)
			if DEBUG:
				cv.putText(image, f"Y:{yaw_step_target}, P:{pitch_step_target}", (detection_left_right_mid_point-10,detection_up_down_mid_point-10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
			
			if yaw_step_target < yaw_motor.current_target - model_params.det_move_threshold_yaw or yaw_step_target > yaw_motor.current_target + model_params.det_move_threshold_yaw:
				if DEBUG: print("got a yaw move")
				yaw_motor.go_to_position(yaw_step_target)
			else:
				if DEBUG: print("yaw move under movement threshold")
			
			if pitch_step_target < pitch_motor.current_target - model_params.det_move_threshold_pitch or pitch_step_target > pitch_motor.current_target + model_params.det_move_threshold_pitch:
				if DEBUG: print("got a pitch move")
				pitch_motor.go_to_position(pitch_step_target)
			else:
				if DEBUG: print("pitch move under movement threshold")
	
	if got_target:
		water_ports.turn_on_ports(port_1=True, port_2=True, port_3=True, port_4=True)
	else:
		water_ports.turn_off_ports(port_1=False, port_2=False, port_3=False, port_4=False)

def turret_controller(queue, event, modelparams, yaw_motor, pitch_motor, water_ports, model_location, shared_lib_location, video_device, output_img_scale):
	#https://github.com/khadas/ksnn/blob/master/docs/ksnn_user_usage_v1.3.pdf
	yolov3 = KSNN('VIM3')
	print("[turret contoller] Starting Turret Controller Thread")
	print(f"[turret contoller] KSNN Version: {yolov3.get_nn_version()}")
	print(shared_lib_location)
	print(model_location)
	print(video_device)
	print("[turret contoller] Init KSNN")
	yolov3.nn_init(c_lib_p = shared_lib_location, nb_p = model_location)
	print("[turret contoller] KSNN ready")
	print("[turret contoller] Setting up video capture")
	cap = cv.VideoCapture(int(video_device))
	cap.set(cv.CAP_PROP_FRAME_WIDTH,FRAME_WIDTH)
	cap.set(cv.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)
	#print("[turret contoller] Set Video resolution: " + str(cap.get(cv.CAP_PROP_FRAME_WIDTH) + " x " + str(cap.get(cv.CAP_PROP_FRAME_HEIGHT))))
	print("[turret contoller] Video capture setup complete")

	frame_start_time = time.time()
	fps = 0
	frames = 0
	total_frame_time = 0

	while not event.is_set():
		#grab a frame from the camera, ret is true if there is a frame grabbed, img is the frame
		ret,img = cap.read()

		if ret:
			if DEBUG: print("[turret contoller] Grabbed a frame")
			start = time.time()
			res_data = yolov3.nn_inference(img, platform='DARKNET', reorder='2 1 0', num=3)
			end = time.time()
			data = res_data.copy()
			del res_data
			
			input0_data = data[0]
			input1_data = data[1]
			input2_data = data[2]

			input0_data = input0_data.reshape(SPAN, LISTSIZE, GRID0, GRID0)
			input1_data = input1_data.reshape(SPAN, LISTSIZE, GRID1, GRID1)
			input2_data = input2_data.reshape(SPAN, LISTSIZE, GRID2, GRID2)

			input_data = list()
			input_data.append(np.transpose(input0_data, (2, 3, 0, 1)))
			input_data.append(np.transpose(input1_data, (2, 3, 0, 1)))
			input_data.append(np.transpose(input2_data, (2, 3, 0, 1)))

			boxes, classes, scores = yolov3_post_process(input_data)

			#resize the image before drawing on it so have a clear overlays for display
			width = int(img.shape[1] * output_img_scale / 100)
			height = int(img.shape[0] * output_img_scale / 100)
			# dsize
			dsize = (width, height)
			# resize image
			img = cv.resize(img, dsize)

			#get target info for the turret
			if boxes is not None:
				get_targets(img, boxes, scores, classes, modelparams, yaw_motor, pitch_motor, water_ports)

			frames = frames + 1
			frame_end_time = time.time()
			total_frame_time = total_frame_time + (frame_end_time - frame_start_time)

			if total_frame_time >= 1:
				fps = (frames / total_frame_time)
				print(f"[turret contoller] ******************************************FPS: {fps:.1f}")
				frames = 0
				total_frame_time = 0
			
			#start the timer for the next frame
			frame_start_time = time.time()
			
			#package the results up to send to the flask thread
			result_data = [img, fps, boxes, scores, classes]
			if queue.full():
				#if the queue is full then take the oldest one out as its a stale frame so no point queing for display
				queue.get()
			#put the latest frame and associated data into the queue to allow the web front end to grab it for display
			queue.put(result_data)

			del data, input0_data, input1_data, input2_data, input_data, boxes, classes, scores

	print("[turret contoller] Tidying up on exit")
	cap.release()
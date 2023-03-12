from flask import Flask, render_template, Response, request, send_from_directory
from camera import VideoCamera
import os
import pickle

from pupil_apriltags import Detector
import cv2
import numpy as np
import apriltag

import pigpio
from gpiozero import Servo

import time
import sys
import threading

'''
####################
    Motor Config
####################
'''
pi = pigpio.pi()

VERT = 19
HORI = 12


curr_angle_vert = 0
curr_angle_hori = 0
# prev_angle_vert = 0
# prev_angle_hori = 0

# 60k to 110k, 85k mid, 50k range, 25k each for +/-
PWM_BASE_VERT = 85 * 1000
PWM_BASE_HORI = 55 * 1000


'''
#############################
    Apriltag & Cam Config
#############################
'''
#cam = cv2.VideoCapture(0)
#cam.set(cv2.CAP_PROP_BUFFERSIZE,1)
#if not cam.isOpened():
#    print("cannot access camera 0")
#    exit()

at_detector = Detector(
   families="tag36h11",
   nthreads=1,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)

print("start detecting")

def init():
    # restet two servos to initial positions
    pi.hardware_PWM(VERT, 50, PWM_BASE_VERT + curr_angle_vert * 1000)
    pi.hardware_PWM(HORI, 50, PWM_BASE_HORI + curr_angle_hori * 1000)

def start(stop_event, args):
    # detect apriltags and uptate servo positions to track each tag
    global curr_angle_vert, curr_angle_hori

pi_camera = VideoCamera(flip=False) # flip pi camera if upside down.

# App Globals (do not edit)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') #you can customze index.html here

def gen(camera):
    #get camera frame
    # detect apriltags and uptate servo positions to track each tag
    global curr_angle_vert, curr_angle_hori

    while True:
        frame = camera.get_frame()
        # read from camera
        #if not ret:
        #    sys.exit('cannot read from camera')

        # detect on grayscale
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #gray = cv2.resize(gray, (640, 360))
        #gray = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # if save:
        #     cv2.imwrite("sound.jpg", gray)
        #if args.visualize:
        #    cv2.imshow('frame', gray)

        detections = at_detector.detect(frame)

        # format output
        if len(detections) >= 1:
            for idx in range(len(detections)):
                x = round(detections[idx].center[0])
                y = round(detections[idx].center[1])

                # vertical
                if (y < 270):    # too high
                    curr_angle_vert = max(-25, curr_angle_vert - 1)
                elif (y > 370):  # too low
                    curr_angle_vert = min( 25, curr_angle_vert + 1)

                # horizontal
                if (x > 230):    # too left
                    curr_angle_hori = max(-25, curr_angle_hori - 1)
                elif (x < 130):  # too right
                    curr_angle_hori = min( 25, curr_angle_hori + 1)



                pi.hardware_PWM(VERT, 50, PWM_BASE_VERT + curr_angle_vert * 1000)
                pi.hardware_PWM(HORI, 50, PWM_BASE_HORI + curr_angle_hori * 1000)

                # print tag info
                print('vert:', curr_angle_vert, ' hori:', curr_angle_hori)
                print("Detected tag id[" + str(detections[idx].tag_id), end='] @ ')
                print('x = '  + str(x) +
                    ' y = ' + str(y) )

        if cv2.waitKey(1) == ord('q'):
            pi.hardware_PWM(VERT, 50, 0)
            pi.hardware_PWM(HORI, 50, 0)
            pi.stop()
            camera.release()
            cv2.destroyAllWindows()
            sys.exit()



        #if stop_event.is_set():
        #    pi.hardware_PWM(VERT,50,0)
        #    pi.hardware_PWM(HORI,50,0)
        #    pi.stop()
        #    cam.release()
        #    cv2.destroyAllWindows()
        #    break

        try:
            with open('capture.tmp', 'rb') as f:
                capture = pickle.load(f)
            if capture:
                print('capturing')
                cv2.imwrite("sound.jpg", frame)
                capture = False
                with open('capture.tmp', 'wb') as f:
                    pickle.dump(capture, f)
        except:
            pass

        _ , jpeg = cv2.imencode(".jpg", frame)
        jpeg = jpeg.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Take a photo when pressing camera button
@app.route('/picture')
def take_picture():
    pi_camera.take_picture()
    return "None"

if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False)

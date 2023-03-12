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
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_BUFFERSIZE,1)
if not cam.isOpened():
    print("cannot access camera 0")
    exit()

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


'''
###########################
        Main Loop
###########################
'''
def init():
    # restet two servos to initial positions
    pi.hardware_PWM(VERT, 50, PWM_BASE_VERT + curr_angle_vert * 1000)
    pi.hardware_PWM(HORI, 50, PWM_BASE_HORI + curr_angle_hori * 1000)

def start(event_dict, args):
    # detect apriltags and uptate servo positions to track each tag
    global curr_angle_vert, curr_angle_hori

    while True:
        # read from camera
        ret, frame = cam.read()
        if not ret:
            sys.exit('cannot read from camera')

        # detect on grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (640, 360))
        gray = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if event_dict['capture'].is_set():
            cv2.imwrite("sound.jpg", gray)
            print('writing image...')
            event_dict['capture'].clear()

        if args.visualize:
            cv2.imshow('frame', gray)

        detections = at_detector.detect(gray)

        # format output
        if len(detections) >= 1:
            for idx in range(len(detections)):
                x = round(detections[idx].center[0])
                y = round(detections[idx].center[1])

                # vertical
                if (y < 270):    # too high
                    curr_angle_vert = max(-25, curr_angle_vert - 2)
                elif (y > 370):  # too low
                    curr_angle_vert = min( 25, curr_angle_vert + 2)

                # horizontal
                if (x > 230):    # too left
                    curr_angle_hori = max(-25, curr_angle_hori - 2)
                elif (x < 130):  # too right
                    curr_angle_hori = min( 25, curr_angle_hori + 2)



                pi.hardware_PWM(VERT, 50, PWM_BASE_VERT + curr_angle_vert * 1000)
                pi.hardware_PWM(HORI, 50, PWM_BASE_HORI + curr_angle_hori * 1000)

                # print tag info
                if args.verbose:
                    print('vert:', curr_angle_vert, ' hori:', curr_angle_hori)
                    print("Detected tag id[" + str(detections[idx].tag_id), end='] @ ')
                    print('x = '  + str(x) +
                        ' y = ' + str(y) )

        if cv2.waitKey(1) == ord('q'):
            pi.hardware_PWM(VERT, 50, 0)
            pi.hardware_PWM(HORI, 50, 0)
            pi.stop()
            cam.release()
            cv2.destroyAllWindows()
            sys.exit()

        if event_dict['stop'].is_set():
            pi.hardware_PWM(VERT,50,0)
            pi.hardware_PWM(HORI,50,0)
            pi.stop()
            cam.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    init()
    start(True)
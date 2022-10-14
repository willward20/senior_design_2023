#!/usr/bin/python3
import os
import cv2 as cv
from vidstab.VidStab import VidStab
import servo1 as servo
import motor
import RPi.GPIO as GPIO
import pygame
import csv
from datetime import datetime


# create data storage
image_dir = 'data' + datetime.now().strftime("%Y-%m-%d-%H-%M") + '/images/'
if not os.path.exists(image_dir):
    try:
        os.makedirs(image_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
# initialize devices
pygame.display.init()
pygame.joystick.init()
pygame.joystick.Joystick(0).init()
stabilizer = VidStab()
cap = cv.VideoCapture(0) #video capture from 0 or -1 should be the first camera plugged in. If passing 1 it would select the second camera
cap.set(cv.CAP_PROP_FPS, 10)
i = 0  # image index
action = [0., 0.]

while True:
    ret, frame = cap.read()   
    if frame is not None:
        # cv.imshow('frame', frame)  # debug
        frame = cv.resize(frame, (int(frame.shape[1]/8), int(frame.shape[0]/8))) 
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    stabilized_frame = stabilizer.stabilize_frame(input_frame=gray,smoothing_window=4)
    if stabilized_frame is None:
        break

    #get thorttle and steering values from joysticks.
    pygame.event.pump()
    throttle = round((pygame.joystick.Joystick(0).get_axis(1)),2)
    motor.drive(throttle)
    steer = (pygame.joystick.Joystick(0).get_axis(3))
    servo.turn(steer)
    action = [throttle, steer]
    # print(f"action: {action}") # debug
    # save image
    cv.imwrite(image_dir + str(i)+'.jpg', gray)
    # save labels
    label = [str(i)+'.jpg'] + list(action)
    label_path = os.path.join(os.path.dirname(os.path.dirname(image_dir)), 'labels.csv')
    with open(label_path, 'a+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(label)  # write the data

    if cv.waitKey(1)==ord('q'):
        break
    i += 1
        

#!/usr/bin/python3
import cv2 as cv
import servo1 as servo
import motor
from torchvision.io import read_image
from torchvision.transforms import ToTensor, Resize
import torch
from cnn_network import cnn_network
from adafruit_servokit import ServoKit
import json ###################################################################################################################

#pca.frequency = 50
kit = ServoKit(channels=16)

################################################################################################################################
# Load in configuration constants for throttle and steering
f = open('config.json')
data = json.load(f)
steering_trim = data['steering_trim']
throttle_lim = data['throttle_trim']
################################################################################################################################

# Load model
model = cnn_network()
model.load_state_dict(torch.load("model_cnn.pth", map_location=torch.device('cpu')))

# Setup Transforms
img2tensor = ToTensor()
resize = Resize(size=(640, 480))

# Create video capturer
cap = cv.VideoCapture(0) #video capture from 0 or -1 should be the first camera plugged in. If passing 1 it would select the second camera
# cap.set(cv.CAP_PROP_FPS, 10)


while True:
    ret, frame = cap.read()   
    if frame is not None:
        # cv.imshow('frame', frame)  # debug
        frame = cv.resize(frame, (int(frame.shape[1]), int(frame.shape[0])))
        print(f"frame size: {frame.shape}")
        gray = frame  # we changed this from b&w to color
        img_tensor = img2tensor(gray)
        img_tensor = resize(img_tensor) # I am 90% certain that this line is not needed -- changing the size should not affect predictions
        print(img_tensor.shape)
    with torch.no_grad():
        pred = model(img_tensor.unsqueeze(dim=0)) # This line adds an extra dimension to the image tensor (print shape before and after to observe this effect)
    print(pred)
    steering, throttle = pred[0][0].item(), pred[0][1].item()
    print("steering: ", steering)
    print("throttle: ", throttle)
    motor.drive(throttle * throttle_lim) ########################################### I used the json file ##################################
    print("motor: ", throttle * throttle_lim) ###################################### I used the json file ##################################
    ang = 90 * (1 + steering) + steering_trim ###################################### I used the json file ##################################
    if ang > 180:
        ang = 180
    elif ang < 0:
        ang = 0
    kit.servo[0].angle = ang
    print("ang: ", ang)

    if cv.waitKey(1)==ord('q'):
        motor.stop()
        motor.close()
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
        

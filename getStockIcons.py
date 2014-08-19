import numpy as np
import cv2
from smash_util import *

source = 'falconDitto.mp4'
cap = cv2.VideoCapture(source)

# take first frame of the video
ret,frame = cap.read()

for i in range(1, 1400):
    cap.read()
# hardcode to find start of match now...should be able to find this programmatically
ret, frame = read_and_preprocess_frame(cap, source)
blueFalcon = frame[363:387, 177:200]
pinkFalcon = frame[363:387, 103:126]
cv2.imshow('blueFalcon', blueFalcon)
cv2.imshow('pinkFalcon', pinkFalcon)
cv2.waitKey(0)
# confirm that zero looks correct
cv2.imwrite('smash_resources_v2/blueFalcon', blueFalcon)
cv2.imwrite('smash_resources_v2/pinkFalcon', pinkFalcon)

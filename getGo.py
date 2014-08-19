# find Go and put it into resources
import numpy as np
import cv2

"""
cap = cv2.VideoCapture('falconDitto.mp4')

# take first frame of the video
ret,frame = cap.read()

for i in range(1, 1432):
    cap.read()

ret, frame = cap.read()

go = frame[155:195,242:355]
"""


cap = cv2.VideoCapture('ppu-vs-stab.mp4')

# take first frame of the video
ret,frame = cap.read()

for i in range(1, 70):
    cap.read()

ret, frame = cap.read()

go = frame[310:385, 325:560]


cv2.imshow('go_', go)
cv2.waitKey(0)
# confirm that zero looks correct
cv2.imwrite('smash_resources_v2/go.png', go)



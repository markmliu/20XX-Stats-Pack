# the purpose of this script is to grab the 0 from the first frame of the smash video... save it as a resource
# 0,7,2,4,3,9,6,8,5
# need 1
import numpy as np
import cv2

def grab_and_resize(frame):
    ret = frame[305:333, 150:175]
    ret = cv2.resize(ret, (35,39))
    return ret

cap = cv2.VideoCapture('falconDitto.mp4')

# take first frame of the video
ret,frame = cap.read()

for i in range(1, 1400):
    cap.read()
# hardcode to find start of match now...should be able to find this programmatically
ret, frame = cap.read()
zero = grab_and_resize(frame)
cv2.imshow('zero_', zero)
cv2.waitKey(0)
# confirm that zero looks correct
cv2.imwrite('smash_resources_v2/0.png', zero)

for i in range(1, 100):
    cap.read()

ret, frame = cap.read()
seven = grab_and_resize(frame)
cv2.imshow('seven', seven)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/7.png', seven)

for i in range(1, 550):
    cap.read()

ret, frame = cap.read()
two = grab_and_resize(frame)
cv2.imshow('two', two)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/2.png', two)

for i in range(1, 450):
    cap.read()

ret, frame = cap.read()
four = grab_and_resize(frame)
cv2.imshow('four', four)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/4.png', four)

for i in range(1, 200):
    cap.read()

ret, frame = cap.read()
one = grab_and_resize(frame)
cv2.imshow('one', one)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/1.png', one)

for i in range(1, 300):
    cap.read()

ret, frame = cap.read()
three = grab_and_resize(frame)
cv2.imshow('three', three)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/3.png', three)

for i in range(1, 500):
    cap.read()

ret, frame = cap.read()
nine = grab_and_resize(frame)
cv2.imshow('nine', nine)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/9.png', nine)

for i in range(1, 900):
    cap.read()

ret, frame = cap.read()
six = grab_and_resize(frame)
cv2.imshow('six', six)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/6.png', six)

for i in range(1, 150):
    cap.read()

ret, frame = cap.read()
eight = grab_and_resize(frame)
cv2.imshow('eight', eight)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/8.png', eight)

for i in range(1, 300):
    cap.read()

ret, frame = cap.read()
five = grab_and_resize(frame)
cv2.imshow('five', five)
cv2.waitKey(0)
cv2.imwrite('smash_resources_v2/5.png', five)

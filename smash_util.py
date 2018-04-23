import cv2
import numpy as np

def is_close_to(p1,p2):
    if abs(p1[0]-p2[0])<5 and abs(p1[1]-p2[1])<5:
        return True

def find_zeros(frame, zero, diff_method):
    #given frame and zero template, find top two matching locations using
    #cv2.matchTemplate
    diff = cv2.matchTemplate(frame, zero, eval(diff_method))
    cv2.imshow('diff', diff)
    cv2.waitKey(0)
    # flatten out the diff array so we can sort it
    diff2 = np.reshape(diff, diff.shape[0]*diff.shape[1])
    # sort in reverse order
    sort = np.argsort(-diff2)
    #print "diff2: " + str(diff2)
    print "sort: " + str(sort)
    ret = []
    (y1, x1) = (np.unravel_index(sort[0], diff.shape)) #best match
    ret.append((x1, y1))
    print "point 1:", diff[y1][x1]
    y2 = y1
    x2 = x1
    idx = 1
    # make sure second point is far enough away from first point
    while abs(y2 - y1) < 5 and abs(x2 - x1) < 5:
        (y2, x2) = (np.unravel_index(sort[idx], diff.shape)) #second best match
        idx += 1

    print "point 2:", diff[y2][x2], " at idx ", idx
    ret.append((x2, y2))
    y3 = y2
    x3 = x2

    # if top two matches are not that high, return false
    if diff[y2][x2] < 0.6:
        return None
    print x1,y1
    print x2,y2

    print "ret: " + str(ret)
    return ret

def load_resources():
    # grab resources and put them into number_templates
    number_templates = []
    for i in range(0,10):
        number_templates.append(cv2.imread('smash_resources_v2/' + str(i) + '.png', 1))
    return number_templates

def read_and_preprocess_frame(cap, source):
    # preprocess frame depending on source...
    # assuming frame is in top 480 x 640 rectangle, chop just that
    ret, frame = cap.read()
    if ret == True:
        if source == 'mangoFalco.mp4':
            frame = frame[0:479, 0:639]
        elif source == 'falconDitto.mp4':
            #its only 360 x 480
            frame = frame[0:359, 81:560]
            frame = cv2.resize(frame, (640, 480))
        elif source == 'ppu-vs-stab.mp4':
            #its 720 x 960
            frame = frame[0:719, 0:959]
            frame = cv2.resize(frame, (640, 480))
    return ret, frame

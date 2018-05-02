import numpy as np
import cv2
import cv2.cv as cv
import sys
import os
from smash_util import *

def get_args(argv):
    if len(argv) < 2:
      print 'python generate_training_data.py <filename> <frames to skip> <num_samples>'
      sys.exit()

    file_name = sys.argv[1]
    frames_to_start = int(sys.argv[2])
    num_samples = int(sys.argv[3])

    return file_name, frames_to_start, num_samples

SKIP_FRAMES=30

def main(argv = sys.argv):
    file_name, frames_to_start, num_samples = get_args(argv)

    # is 1400, for falconDitto, 150 for mangoFalco

    cap = cv2.VideoCapture(file_name)

    fps = cv.GetCaptureProperty(cv.CaptureFromFile(file_name),
                                cv.CV_CAP_PROP_FPS)
    print "Frames Per Second: " + str(fps)
    # hardcode to find start of match now...should be able to find this
    # programmatically
    for i in xrange(frames_to_start):
        cap.grab()
    ret, frame = read_and_preprocess_frame(cap, file_name)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)
    for i in xrange(num_samples):
        ret, frame = read_and_preprocess_frame(cap, file_name)
        cv2.imwrite('training/frame%d.jpg'%i, frame)
        for j in xrange(SKIP_FRAMES):
            cap.grab()

if __name__ == "__main__":
    main()

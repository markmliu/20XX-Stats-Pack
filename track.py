import numpy as np
import cv2
import sys
import os
from smash_util import *

def get_args(argv):
    if len(argv) < 2:
      print 'python track.py <filename> <frames to skip> '
      sys.exit()

    file_name = sys.argv[1]
    frames_to_start = int(sys.argv[2])

    return file_name, frames_to_start

def get_tracker(tracker_type, minor_ver):
    if int(minor_ver) < 3:
        tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            # woks for ~10 frames, decently robust
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            # not quite as good as boosting
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            # works for 2 frames
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            # does some weird stufff where it changes object size by a lot
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            # 2 frames
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            # crashes?
            tracker = cv2.TrackerGOTURN_create()
    return tracker

def get_fps(cap, major_ver):
    if int(major_ver)  < 3 :
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        print "Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps)
    else :
        fps = cap.get(cv2.CAP_PROP_FPS)
        print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)
    return fps

def main(argv = sys.argv):
    # is 1400, for falconDitto
    file_name, frames_to_start = get_args(argv)
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    cap = cv2.VideoCapture(file_name)
    fps = get_fps(cap, major_ver)
    for i in xrange(frames_to_start):
        cap.grab()
    ret, frame = cap.read()
    initial_bbox = cv2.selectROI(frame, False)
    cap.release()

    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW']
    # tracker_types = ['KCF', 'TLD', 'MEDIANFLOW']
    for tracker_type in tracker_types:
        #  get a fresh cap.
        cap = cv2.VideoCapture(file_name)
        for i in xrange(frames_to_start):
            cap.grab()
        ret, frame = cap.read()

        w = int(cap.get(3))
        h = int(cap.get(4))
        print "w: ", w
        print "h: ", h
        print "tracker type: ", tracker_type
        tracker = get_tracker(tracker_type, minor_ver)
        print "created tracker!"
        out = cv2.VideoWriter(tracker_type + '.avi',
                      cv2.VideoWriter_fourcc(*'XVID'), 30.0, (w, h))

        # Initialize tracker with first frame and bounding box
        ok = tracker.init(frame, initial_bbox)
        # bbox is of form: xmin, ymin, x offset, y offset
        # rectangle takes top_left, bottom_right

        top_left = (int(initial_bbox[0]), int(initial_bbox[1]))
        bottom_right = (int(initial_bbox[0] + initial_bbox[2]),
                        int(initial_bbox[1] + initial_bbox[3]))

        cv2.rectangle(frame, top_left, bottom_right, 255, 2)

        cv2.imshow('frame', frame)
        cv2.waitKey(0)

        frames_elapsed = 0
        # capture up to 5 seconds
        while(cap.isOpened() and frames_elapsed < (fps * 5)):

            ret, frame = cap.read()

            ok, bbox = tracker.update(frame)
            # Draw bounding box
            if ok:
                # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
            else :
                # Tracking failure
                cv2.putText(frame, "Tracking failure detected", (100,80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
            # Display tracker type on frame
            cv2.putText(frame, tracker_type + " Tracker", (100,20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);

            cv2.imshow('frame', frame)
            out.write(frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            frames_elapsed += 1
        out.release()
        cv2.destroyAllWindows()
        cap.release()

if __name__ == "__main__":
    main()

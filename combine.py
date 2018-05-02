import numpy as np
import cv2
import sys
import os

def main(argv = sys.argv):
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW']
    file_names = [type + '.avi' for type in tracker_types]
    caps = [cv2.VideoCapture(file_name) for file_name in file_names]
    first = True
    w = int(caps[0].get(3))
    h = int(caps[0].get(4))
    # output will be video frames combined, so 2 * h and 3 * w
    out = cv2.VideoWriter('combined.avi',
                          cv2.VideoWriter_fourcc(*'XVID'), 30.0,
                          (3 * w, 2 * h))
    while caps[0].isOpened():
        rets, frames = zip(*[cap.read() for cap in caps])
        if any(not ret for ret in rets):
            break
        # add a dummy for nice stacking.
        dummy = np.zeros(frames[4].shape, np.uint8)

        col1 = np.vstack((frames[0], frames[1]))
        col2 = np.vstack((frames[2], frames[3]))
        col3 = np.vstack((frames[4], dummy))
        all = np.hstack((col1, col2, col3))

        cv2.imshow('all', all)
        out.write(all)
        if first:
            cv2.waitKey(0)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        first = False
    out.release()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

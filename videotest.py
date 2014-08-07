import numpy as np
import Pycluster
import cv2
from matplotlib import pyplot as plt

cap = cv2.VideoCapture('friendly6.mp4')

while(cap.isOpened()):
    ret, frame = cap.read()

    orb = cv2.ORB(edgeThreshold=70)
    kp = orb.detect(frame,None)
    kp, des = orb.compute(frame, kp)
    kpp = [x.pt for x in kp]
    kpp_list = np.array(kpp,np.float32)
    temp, classified_pts, means = cv2.kmeans(data=np.asarray(kpp_list),
        K=2,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 20), 
        attempts = 5, 
        flags = cv2.KMEANS_RANDOM_CENTERS)

    for point, allocation in zip(kpp_list, classified_pts):
        if allocation == 0:
            color = (255,0,0)
        elif allocation == 1:
            color = (0,0,255)
        #cv2.circle(frame, (int(point[0]),int(point[1])), 1, color,-1)
    cv2.circle(frame,(int(means[0][0]),int(means[0][1])),5,(0,255,0),-1)
    cv2.circle(frame,(int(means[1][0]),int(means[1][1])),5,(255,0,0),-1)

    #frame = cv2.drawKeypoints(frame, [kp[x] where allocation[x]==0],color = (0,255,0), flags=0)

    cv2.imshow('frame',frame)
    if cv2.waitKey(250) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
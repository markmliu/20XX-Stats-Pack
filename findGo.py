# the purpose of this script is to find the "GO" image and draw a box around it
# finding "GO" marks the beginning of the match

# method
# search first three minutes of video, if you cant find it by then, forget searching the rest and just try a smaller
# "GO" template
#
#   found_start = false
#
#   while(found_start == false)
#       for three minutes of frames:
#           for each frame as i:
#               if (matchtemplate(frame,go_template) == true)
#                   print "match starts frame: " + i
#                   found_start = true
#           if(found_start == false)
#               size_down(go_template)


import numpy as np
import cv2

FPS = 30
DIFF_METHOD = 'cv2.TM_CCOEFF_NORMED'
DIFF_THRESHOLD = 0.9

cap = cv2.VideoCapture('falconDitto.mp4')

go_template = cv2.imread('smash_resources_v2/go.png', 1)
_, w, h = go_template.shape[::-1]


cv2.imshow('go', go_template)

#jump jump past the first few seconds of no match (lessen wait time for tests)
for i in range(1, 1350):
    cap.read()

firstFrame = -1

for i in range(1, 150):
    ret,frame = cap.read()

    diff = cv2.matchTemplate(frame, go_template, eval(DIFF_METHOD))

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(diff)

    #print max_val

    if max_val > DIFF_THRESHOLD:
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(frame,top_left, bottom_right, 255, 2)

        if firstFrame == -1:
            firstFrame = i
        lastFrame = i

    cv2.imshow('video', frame)

    cv2.waitKey(1)

print "\"Go!\" detected on frames: " + str(firstFrame) + " to " + str(lastFrame)

# release the capture
cap.release()
cv2.destroyAllWindows()
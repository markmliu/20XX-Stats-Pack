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

import math
import cv2


FPS = 30
DIFF_METHOD = 'cv2.TM_CCOEFF_NORMED'
DIFF_THRESHOLD = 0.9

#cap = cv2.VideoCapture('falconDitto.mp4')
cap = cv2.VideoCapture('ppu-vs-stab.mp4')
ret,frame = cap.read()
vheight, vwidth = frame.shape[:2]

print str(vwidth/3) + " " + str(vheight/3)

go_template = cv2.imread('smash_resources_v2/go.png', 1)



def reduceByX(frame, pixels):
    _, w, h = frame.shape[::-1]

    ratio = w/h
    w = w - pixels;
    h = int(math.floor(w/ratio))

    ret = cv2.resize(frame, (w,h))
    return ret



_, w, h = go_template.shape[::-1]
go_template = cv2.resize(go_template, (w/2, h/2))

#jump jump past the first few seconds of no match (lessen wait time for tests)
#for i in range(1, 1350):
#    cap.read()

firstFrame = -1

while firstFrame == -1:

    for i in range(1, FPS*5):
        ret,frame = cap.read()

        # later, calculate what it takes to make the image 240p
        resizeAmount = 3
        frame = cv2.resize(frame, (vwidth/resizeAmount, vheight/resizeAmount))

        diff = cv2.matchTemplate(frame, go_template, eval(DIFF_METHOD))

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(diff)

        #print max_val

        if max_val > DIFF_THRESHOLD:
            top_left = max_loc
            bottom_right = (top_left[0] + (w/resizeAmount), top_left[1] + (h/resizeAmount))
            cv2.rectangle(frame,top_left, bottom_right, 255, 2)

            if firstFrame == -1:
                firstFrame = i
            lastFrame = i

        cv2.imshow('video', frame)

        cv2.waitKey(1)

    if firstFrame == -1:
        print "Couldnt find \"Go!\"..."
        print "resizing go"
    else:
        print "\"Go!\" detected on frames: " + str(firstFrame) + " to " + str(lastFrame)

    go_template = reduceByX(go_template, 3)
    cv2.imshow('newgo', go_template)

    #ideally we'd want to just jump to frame 0 again, but having trouble figuring that one out
    cap = cv2.VideoCapture('ppu-vs-stab.mp4')
    #cap = cv2.VideoCapture('falconDitto.mp4')

# release the capture
cap.release()
cv2.destroyAllWindows()
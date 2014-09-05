from multiprocessing import Process, Manager
import time
import cv2


class StreamFeed(object):

    def __init__(self):
        manager = Manager()
        frame_list = manager.list([None])
        self.frame_list = frame_list
        self.started = False

    def StartStreaming(self, video_name):
        if self.started:
            print "Stream already started!"
            return
        p = Process(target = _stream_video, args = (video_name, self.frame_list))
        p.start()
        self.started = True

    def GetFrame(self):
        if not self.started: return False, None

        try:
            value = self.frame_list[0]
        except:
            return False, None

        if value is None: return False, None
        return True, value


def _stream_video(video_name, frame_list, frame_delay = 0.025):
    cap = cv2.VideoCapture(video_name)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == False:
            break
        if _write_frame(frame,frame_list) == False:
            break

        time.sleep(frame_delay) # wait ms to simulate a video input stream

    cap.release()
    _write_frame(None, frame_list)
    return

def _write_frame(value, frame_list):
    try:
        frame_list[0] = value
    except:
        return False


# ======= example usage: ========

# simulate a heavy process that takes 0.25 seconds
# so you can only sample the video every .25 seconds
if __name__ == '__main__':
    stream = StreamFeed()

    stream.StartStreaming('falconDittoTrim.mp4')

    # wait until it's started
    ret, frame = stream.GetFrame()
    while ret is False:
        time.sleep(0.010) 
        ret, frame = stream.GetFrame()

    while ret != False:

    # --- Example operations
        # wait to simulate heavy processing
        time.sleep(0.25) 

        # Display the resulting frame
        cv2.imshow('frame',frame)
        cv2.waitKey(1)

        ret, frame = stream.GetFrame()

    cv2.destroyAllWindows()



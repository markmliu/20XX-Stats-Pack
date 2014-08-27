from multiprocessing import Process, Manager
import time
import cv2
import pickle


def _stream_video(video_name, frame_list):
    cap = cv2.VideoCapture(video_name)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == False:
            break
        if _write_frame(frame,frame_list) == False:
            break

        time.sleep(0.025) # wait ms to simulate a video input stream

    cap.release()
    _write_frame(None, frame_list)
    return

def _write_frame(value, frame_list):
    try:
        frame_list[0] = value
    except:
        return False


class StreamFeed(object):

    def __init__(self):
        manager = Manager()
        frame_list = manager.list([None])
        self.frame_list = frame_list

    def StartStreaming(self, video_name):
        p = Process(target = _stream_video, args = (video_name, self.frame_list))
        p.start()

    def GetFrame(self):
        try:
            value = self.frame_list[0]
        except:
            return None

        return value


# ======= example usage: ========

if __name__ == '__main__':
    stream = StreamFeed()

    stream.StartStreaming('falconDittoTrim.mp4')

    # wait until it's started
    frame = stream.GetFrame()
    while frame is None:
        time.sleep(0.010) 
        frame = stream.GetFrame()

    
    while frame is not None:

    # --- Example operations
        # wait to simulate heavy processing
        time.sleep(0.25) 

        # Display the resulting frame
        cv2.imshow('frame',frame)
        cv2.waitKey(25)

        frame = stream.GetFrame()

    cv2.destroyAllWindows()



import datetime
import os
import time
import glob
import threading
import sys
import shutil
import argparse

import cv2


class Camera:
    def __init__(self, dev_num=0, h=None, w=None, interval=0.5, save_dir=None):
        self.cap = cv2.VideoCapture(dev_num)

        if self.cap.isOpened():
            print("ok device {}".format(dev_num))
            save_dir = save_dir or "./monitor"
            self.dev_num = dev_num
            self.movie_save_dir = os.path.join(save_dir, "dev{}".format(dev_num))
            self.interval = interval
            if h and w:
                self.cap.set(3, w)
                self.cap.set(4, h)
            self.h = int(self.cap.get(4))
            self.w = int(self.cap.get(3))
        else:
            print("no device")

    def __call__(self):
        if not self.cap.isOpened():
            print("no device")
            return None
        try:
            print("start capture")
            pic_list = []
            past = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            font = cv2.FONT_HERSHEY_PLAIN
            while(True):
                ret, frame = self.cap.read()
                if ret:
                    if frame.mean() > 50:
                        time_text = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                        if time_text[:13] != past[:13]:
                            self.del_history()
                            save_dir = os.path.join(self.movie_save_dir, past[:10])
                            os.mkdir(save_dir)
                            maker = threading.Thread(target=self.make_avi, args=(pic_list, os.path.join(save_dir, past[:13]+".avi")))
                            maker.start()
                            pic_list = []
                        sys.stderr.write("\rcapture {}".format(time_text))
                        frame = cv2.putText(frame, time_text, (self.w - 120, self.h - 20), font, 0.6, (0, 0, 255))
                        pic_list.append(frame)
                        past = time_text
                        time.sleep(self.interval)
                else:
                    print("no device")
                    break

        except KeyboardInterrupt :
            print("end capture")
            self.cap.release()

    def make_avi(self, pic_list, save_name):
        out = cv2.VideoWriter(save_name, (cv2.VideoWriter_fourcc("M", "J", "P", "G")), 60, (self.w, self.h))
        if not out.isOpened():
            print("can not get...")
            return False
        for pic in pic_list:
            out.write(pic)
        sys.stderr.write("\rsave done {} pic                \n ".format(len(pic_list)))
        out.release()

    def sub(self, ksize=3, pic_list=None, save_name="aa.avi"):
        out = cv2.VideoWriter(save_name, (cv2.VideoWriter_fourcc("M", "J", "P", "G")), 10, (self.w, self.h))
        mog = cv2.createBackgroundSubtractorMOG2()
        if not pic_list:
            pic_list = glob.glob(os.path.join(self.save_dir, "*"))
            pic_list.sort()
        if not out.isOpened():
            print("can not get...")
            return False
        for i in pic_list:
            pic = cv2.imread(i)
            pic = mog.apply(pic)
            pic = cv2.cvtColor(pic, cv2.COLOR_GRAY2BGR)
            pic = cv2.medianBlur(pic, ksize=ksize)
            out.write(pic)
        print("done {} pic ".format(len(pic_list)))
        out.release()

    def del_history(self, day=7):
        del_dir = datetime.datetime.now() - datetime.timedelta(days=day)
        del_dir_path = os.path.join(self.movie_save_dir, del_dir.strftime("%Y-%m-%d"))
        shutil.rmtree(del_dir_path, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(
    description = 'Monitoring Camera Script with Web Camera')
    parser.add_argument('--devnum', type=int, default=0,
                    help='camera device number')
    parser.add_argument('--interval', type=float, default=0.5,
                    help='snapshot Interval')
    parser.add_argument('--height', type=int, default=0,
                    help='save picture height')
    parser.add_argument('--width', type=int, default=0,
                    help='save picture width')
    parser.add_argument('--save_path', default='monitor',
                    help='movie save dir path')

    args = parser.parse_args()
    camera = Camera(args.devnum, args.height, args.width, args.interval, args.save_path)
    camera()

if __name__ == "__main__":
    main()

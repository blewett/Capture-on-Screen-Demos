"""

capture_demos.py: Original work Copyright (C) 2025 by Blewett

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is a simple system for capturing on screen activities.  This is
used for producing video from on screen demo displays.  This does not
capture audio.  Better video demos add the audio after the demo has
been created.  One might use a program like "audacity" to narrate
demos.  Capture the narration while playing the video - always a better
result than driving and talking.  Add the audio using a program like
"openshot".

Load cv2:
 pip3 install opencv-python

Load tkinter:
 apt-get install python3-tk

Load Pillow:
 pip3 install --upgrade Pillow

and other words like that.

"""
import tkinter as tk
from tkinter import ttk
import threading
import time

from PIL import ImageGrab
from PIL import Image
import cv2
import numpy as np
import time
import os
import sys
from collections import deque

# global queues for communicating frame
global in_queue
global out_queue
global sre
global sde
global canvas_width
global canvas_height

# FIFOqueue for communicating with thread safe queues
class FIFOQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if self.is_empty():
            return None

        item = self.queue.popleft()
        return item

    def printqueue(self):
        print(self.queue)

    def peek(self):
        if self.is_empty():
            return None
        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)
# end FIFOqueue for communicating with thread safe queues

# rectangle class - width, height, count and flag
class rectx:
    def __init__(self, x1, y1, x2, y2):
        if x1 > x2:
            t = x1
            x1 = x2
            x2 = t
        if y1 > y2:
            t = y1
            y1 = y2
            y2 = t
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.calc_width()
        self.count = 0
        self.flag = True

    def addoffset(self, x, y):
        self.x1 += x
        self.x2 += x
        self.y1 += y
        self.y2 += y
        self.calc_width()

    def calc_width(self):
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1

    def ptinrect(self, x, y):
        if (x < self.x1):
            return False
        if (y < self.y1):
            return False
        if (x > self.x1 + self.width):
            return False
        if (y > self.y1 + self.height):
            return False
        return True

    def rectinrect(self, r2):
        r1 = self

        if (r1.ptinrect(r2.x1, r2.y1) and 
            r1.ptinrect(r2.x1 + r2.width, r2.y1 + r2.height)):
            return True

        return False

    def normalize_rect(self):
        ret = True
        if self.x1 > self.x2:
            t = self.x1
            self.x1 = self.x2
            self.x2 = t
            ret = False
        if self.y1 > self.y2:
            t = self.y1
            self.y1 = self.y2
            self.y2 = t
            ret = False
        return ret

    def print(self):
        print("select_rect = rectx(" +
              str(self.x1) + ", " +
              str(self.y1) + ", " +
              str(self.x2) + ", " +
              str(self.y2) +")")
              
        print("self.width = " + str(self.width) + "\n" +
              "self.height = " + str(self.height))

# end of rectangle class


# offset class - x and y of the screen
class offsetPt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def print(self):
        print("offset x = " + str(self.x) + "\n" +
              "offset y = " + str(self.y))

# end of offset class

# globals for selecting rectangles
global select_rect
global offset
global fps

select_rect = rectx(0,0,0,0)
offset = offsetPt(0,0)
fps = 16

# selecting rectangles from the screen - data and code
def start_drawing(event):
    global canvas
    global select_rect

    select_rect.x1 = event.x
    select_rect.y1 = event.y

def draw_rectangle(event):
    global canvas
    global select_rect

    canvas.delete("rectangle")
    canvas.create_rectangle(select_rect.x1, select_rect.y1,
                            event.x, event.y, tags="rectangle")

def end_drawing(event):
    global canvas
    global select_rect
    global toplevel
    global sre

    select_rect.x2 = event.x
    select_rect.y2 = event.y
    select_rect.calc_width()

    canvas.create_rectangle(select_rect.x1, select_rect.y1,
                            select_rect.x2, select_rect.y2,
                            tags="rectangle")

    offset.x = canvas.winfo_rootx()
    offset.y = canvas.winfo_rooty()

    select_rect.addoffset(offset.x, offset.y)

    sre.entry_x1.delete(0, "end")
    sre.entry_x1.insert(0, select_rect.x1)

    sre.entry_y1.delete(0, "end")
    sre.entry_y1.insert(0, select_rect.y1)

    sre.entry_x2.delete(0, "end")
    sre.entry_x2.insert(0, select_rect.x2)

    sre.entry_y2.delete(0, "end")
    sre.entry_y2.insert(0, select_rect.y2)


def create_canvas(toplevel):
    global canvas
    global select_rect

    toplevel.title("Select an Area and then close the window (X) -->")
    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    canvas = tk.Canvas(toplevel, width=canvas_width, height=canvas_height)
    canvas.pack()

    canvas.bind("<Button-1>", start_drawing)
    canvas.bind("<B1-Motion>", draw_rectangle)
    canvas.bind("<ButtonRelease-1>", end_drawing)

    toplevel.wait_visibility(toplevel)
    toplevel.wm_attributes('-alpha', 0.5)

    return canvas


class Select_video_area:

    def on_toplevel_closing(self):
        self.toplevel.destroy()
        self.set_rectx_button.config(state=tk.NORMAL)

    def __init__(self, toplevel, set_rectx_button):

        global canvas
        global select_rect
        global offset
        global canvas_width
        global canvas_height

        self.set_rectx_button = set_rectx_button
        self.toplevel = toplevel

        canvas = create_canvas(toplevel)

        toplevel_screen_width = toplevel.winfo_screenwidth()
        toplevel_screen_height = toplevel.winfo_screenheight()
        
        x = int (round (toplevel_screen_width - canvas_width) / 2)
        y = int (round (toplevel_screen_height - canvas_height) / 2)

        toplevel.geometry(str(canvas_width) + "x" + str(canvas_height) +
                          "+" + str(x) + "+" + str(y))

        toplevel.protocol("WM_DELETE_WINDOW", self.on_toplevel_closing)


# end of selecting rectangles from the screen

# FPS_Video_count class - writes video captured from the screen for demos
class FPS_Video_calc:

    def __init__(self, calc_fps_button):

        global fps

        self.calc_fps_button = calc_fps_button
        self.total_frames = fps * 5

        # VideoWriter constructors
        #.mp4 = codec id 2
        #label_text = "count"
        self.recording_filename = "countfps.avi"

        #fourcc = cv2.VideoWriter_fourcc(*'I420') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'MP4V') # .avi
        fourcc = cv2.VideoWriter_fourcc(*'MP42') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'AVC1') # error libx264
        #fourcc = cv2.VideoWriter_fourcc(*'H264') # error libx264
        #fourcc = cv2.VideoWriter_fourcc(*'WRAW') # error --- no information ---
        #fourcc = cv2.VideoWriter_fourcc(*'MPEG') # .avi 30fps
        #fourcc = cv2.VideoWriter_fourcc(*'MJPG') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'XVID') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'H265') # error 

        #
        # collect and write the video
        #
        self.recording_writer = cv2.VideoWriter(self.recording_filename, fourcc, fps, (select_rect.width, select_rect.height))
        self.out_queue = FIFOQueue()
        threading.Thread(target=self.update_fps, daemon=True).start()

    # FPS_Video_count loop
    def update_fps(self):

        global sre
        global fps

        num_frames_read = 0
        started = False
        start = time.time()

        while num_frames_read < self.total_frames:

            screen = np.array(ImageGrab.grab(bbox=(select_rect.x1,
                                                   select_rect.y1,
                                                   select_rect.x2,
                                                   select_rect.y2)))

            if self.recording_writer and self.recording_writer.isOpened():
                #cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                #recording_writer.write(screen)
                cv_img = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
                self.recording_writer.write(cv_img)

            num_frames_read +=1

        self.recording_writer.release() 
        os.unlink(self.recording_filename)

        # calculate FPS
        end = time.time()
        # bias toward longer
        seconds = round((end - start) + 1.5)
        fps = round(num_frames_read / seconds) & (~1)

        """
        print("approx. running time: " + str(seconds))
        print("approx. frames writen per second: " + str(fps))
        print("num_frames_read = " + str(num_frames_read))
        """

        sre.entry_fps.delete(0, "end")
        sre.entry_fps.insert(0, str(fps))

        self.calc_fps_button.config(state=tk.NORMAL)

# end of FPS_Video_count class


# WriteVideo class - writes video captured from the screen for demos
class WriteVideo:

    def __init__(self, select_rect, in_queue, out_queue):

        self.select_rect = select_rect
        self.in_queue = in_queue
        self.out_queue = out_queue
        global fps

        # VideoWriter constructors
        #.mp4 = codec id 2
        label_text = "test"
        recording_filename = time.strftime(label_text +
                                           "-%d-%m-%Y-%H-%M-%S.avi")

        #fourcc = cv2.VideoWriter_fourcc(*'I420') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'MP4V') # .avi
        fourcc = cv2.VideoWriter_fourcc(*'MP42') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'AVC1') # error libx264
        #fourcc = cv2.VideoWriter_fourcc(*'H264') # error libx264
        #fourcc = cv2.VideoWriter_fourcc(*'WRAW') # error --- no information ---
        #fourcc = cv2.VideoWriter_fourcc(*'MPEG') # .avi 30fps
        #fourcc = cv2.VideoWriter_fourcc(*'MJPG') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'XVID') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'H265') # error 

        #
        # collect and write the video
        #
        self.recording_writer = cv2.VideoWriter(recording_filename, fourcc, fps,
                                           (select_rect.width, select_rect.height))
        threading.Thread(target=self.write_video, daemon=True).start()

    # writer loop
    def write_video(self):
        num_frames_read = 0
        queues_count = 0
        started = False
        start = time.time()
        start_time = None

        loop_test = True
        while loop_test == True:
            self.data = self.in_queue.dequeue()
            if self.data == "stop":
                started = False
                self.out_queue.enqueue("stopped")
                loop_test = False
                continue

            if self.data == "start":
                started = True
                self.out_queue.enqueue("recv start")
                start_time = time.time()

            if started == False:
                time.sleep(1)
                continue

            screen = np.array(ImageGrab.grab(bbox=(select_rect.x1,
                                                   select_rect.y1,
                                                   select_rect.x2,
                                                   select_rect.y2)))

            if self.recording_writer and self.recording_writer.isOpened():
                #cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                #recording_writer.write(screen)
                cv_img = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
                self.recording_writer.write(cv_img)

            num_frames_read +=1
            queues_count += 1
            if queues_count >= 20:
                self.out_queue.enqueue(str(num_frames_read))
                queues_count = 0


        self.recording_writer.release() 

        # calculate FPS
        end = time.time()
        seconds = round(end - start_time) & (~1)
        if seconds > 0:
            fps = round(num_frames_read / seconds) & (~1)
        else:
            fps = 0

        """
        print()
        print("approx. running time: " + str(seconds))
        print("approx. frames writen per second: " + str(fps))
        print("num_frames_read = " + str(num_frames_read))
        """

# end of WriteVideo class

def check_select_rect():
    global select_rect
    global sre

    if select_rect.normalize_rect() == False:
        sre.entry_x1.delete(0, "end")
        sre.entry_x1.insert(0, select_rect.x1)

        sre.entry_y1.delete(0, "end")
        sre.entry_y1.insert(0, select_rect.y1)

        sre.entry_x2.delete(0, "end")
        sre.entry_x2.insert(0, select_rect.x2)

        sre.entry_y2.delete(0, "end")
        sre.entry_y2.insert(0, select_rect.y2)


def test_value(new_value):
    if new_value == "":
        return True

    if len(new_value) > 4:
        return False
    
    if new_value.isdigit() == False:
        return False

    if int(new_value) == 0:
        return False

    return True
    

def validate_select_entry_x1(new_value):
    global select_rect

    if new_value == "":
        return True
    if test_value(new_value) == False:
        return False
    select_rect.x1 = int(new_value)
    return True

def validate_select_entry_y1(new_value):
    global select_rect

    if new_value == "":
        return True
    if test_value(new_value) == False:
        return False
    select_rect.y1 = int(new_value)
    return True

def validate_select_entry_x2(new_value):
    global select_rect

    if new_value == "":
        return True
    if test_value(new_value) == False:
        return False
    select_rect.x2 = int(new_value)
    return True

def validate_select_entry_y2(new_value):
    global select_rect

    if new_value == "":
        return True
    if test_value(new_value) == False:
        return False
    select_rect.y2 = int(new_value)
    return True

def validate_fps_entry(new_value):
    global fps
    global sre

    if new_value == "":
        return True

    if len(new_value) > 2:
        return False
    
    if new_value.isdigit() == False:
        return False

    if int(new_value) == 0:
        return False

    fps = int(new_value)

    return True

class DataEntries():

    def __init__(self, data_frame):

        self.data_frame = data_frame

        #
        # time
        self.label_time = ttk.Label(self.data_frame, text="approx. time:")
        self.label_time.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.entry_time = ttk.Entry(self.data_frame, width=10)
        self.entry_time.grid(row=0, column=1, padx=5, pady=5, ipadx=5, sticky='w')
        
        #
        # frames
        self.label_frames = ttk.Label(self.data_frame, text="frame count:")
        self.label_frames.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        
        self.entry_frames = ttk.Entry(self.data_frame, width=10)
        self.entry_frames.grid(row=1, column=1, padx=5, pady=5, ipadx=5, sticky='w')


class SelectRectEntries():

    def __init__(self, frame):

        self.frame = frame

        validate_select_x1 = frame.register(validate_select_entry_x1)
        validate_select_y1 = frame.register(validate_select_entry_y1)
        validate_select_x2 = frame.register(validate_select_entry_x2)
        validate_select_y2 = frame.register(validate_select_entry_y2)
        validate_fps = frame.register(validate_fps_entry)

        ttk.Label(frame, text="selection rectangle = ").grid(row=1, column=0, sticky="e", padx=5, pady=5)

        i = 1
        self.entry_x1 = ttk.Entry(frame, width=4, validate='key', validatecommand=(validate_select_x1, '%P'))
        self.entry_x1.grid(row=1, column=i, padx=5, pady=5)

        i += 1
        self.entry_y1 = ttk.Entry(frame, width=4, validate='key', validatecommand=(validate_select_y1, '%P'))
        self.entry_y1.grid(row=1, column=i, padx=5, pady=5)

        i += 1
        self.entry_x2 = ttk.Entry(frame, width=4, validate='key', validatecommand=(validate_select_x2, '%P'))
        self.entry_x2.grid(row=1, column=i, padx=5, pady=5)

        i += 1
        self.entry_y2 = ttk.Entry(frame, width=4, validate='key', validatecommand=(validate_select_y2, '%P'))
        self.entry_y2.grid(row=1, column=i, padx=5, pady=5)


        ttk.Label(frame, text="frames per second = ").grid(row=3, column=0, sticky="e", padx=5, pady=5)

        self.entry_fps = ttk.Entry(frame, width=2, validate='key', validatecommand=(validate_fps, '%P'))
        self.entry_fps.grid(row=3, column=1)


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        global sre
        global sde
        global fps
        global canvas_width
        global canvas_height

        self.title("Capture on Screen Demos")
        self.running = False

        self.data_frame = ttk.LabelFrame(self)
        self.data_frame.grid(row=0, column=1, padx=5, pady=5)
        sde = DataEntries(self.data_frame)
        
        sde.entry_time.delete(0, "end")
        sde.entry_time.insert(0, "0")

        sde.entry_frames.delete(0, "end")
        sde.entry_frames.insert(0, "0")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=5, columns=2, padx=55, pady=20, sticky='ew')

        self.start_button = ttk.Button(self, text="Start",
                                       command=self.start)
        self.start_button.grid(row=7, columns=6, padx=5, pady=5)

        self.stop_button = ttk.Button(self, text="Stop",
                                      command=self.stop, state=tk.DISABLED)
        self.stop_button.grid(row=8, columns=6, padx=5, pady=5)

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=9, columns=2, padx=55, pady=20, sticky='ew')

        frame = ttk.LabelFrame(self)
        frame.grid(row=14, column=1, padx=5, pady=5)
        sre = SelectRectEntries(frame)

        sre.entry_x1.delete(0, "end")
        sre.entry_x1.insert(0, str(select_rect.x1))

        sre.entry_y1.delete(0, "end")
        sre.entry_y1.insert(0, str(select_rect.y1))

        sre.entry_x2.delete(0, "end")
        sre.entry_x2.insert(0, str(select_rect.x2))

        sre.entry_y2.delete(0, "end")
        sre.entry_y2.insert(0, str(select_rect.y2))

        sre.entry_fps.delete(0, "end")
        sre.entry_fps.insert(0, str(fps))

        self.set_rectx_button = ttk.Button(self, text='sweep out area to be captured',
                                           command=self.set_select_rect)
        self.set_rectx_button.grid(row=12, columns=5, padx=5, pady=5)

        self.calc_fps_button = ttk.Button(self, text='calculate frames per second',
                                         command=self.fps_calc)
        self.calc_fps_button.grid(row=13, columns=5, padx=5, pady=5)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        canvas_width = int (round (screen_width * 0.99))
        canvas_height = int (round (screen_height * 0.99))

        self.in_queue = FIFOQueue()
        self.out_queue = FIFOQueue()
        self.start_time = None
        self.sent_start = False
        self.recved_stopped = False


    def set_select_rect(self):
        global select_rect
        global fps
        self.set_rectx_button.config(state=tk.DISABLED)
        check_select_rect()
        self.toplevel = tk.Toplevel(self)
        Select_video_area(self.toplevel, self.set_rectx_button)

    def fps_calc(self):
        global fps
        self.calc_fps_button.config(state=tk.DISABLED)
        # calc_fps_button.config(state=tk.NORMAL) at the end of FPS_Video_count
        #  which is a daemon
        check_select_rect()
        FPS_Video_calc(self.calc_fps_button)

    # app main control loop
    def app_update_thread(self):

        while self.running:
            self.data = self.out_queue.dequeue()
            if self.data == None:
                time.sleep(0.5)
                continue

            if self.data == "stopped":
                sde.entry_frames.delete(0, "end")
                sde.entry_frames.insert(0, "stopped")
                sde.entry_frames.delete(0, "end")
                sde.entry_frames.insert(0, "stopped")
                self.sent_start = False
                self.recved_stopped = True
                self.running = False

            running_time = round(time.time() - self.start_time, 1)

            sde.entry_time.delete(0, "end")
            sde.entry_time.insert(0, str(running_time))

            sde.entry_frames.delete(0, "end")
            sde.entry_frames.insert(0, str(self.data))


    def start(self):
        if not self.running:
            self.running = True
            self.recved_stopped = False
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            check_select_rect()

            WriteVideo(select_rect, self.in_queue, self.out_queue)

            time.sleep(0.5)
            self.in_queue.enqueue("start")
            self.start_time = time.time()
            self.sent_start = True

            threading.Thread(target=self.app_update_thread, daemon=True).start()

    def stop(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.in_queue.enqueue("stop")
        self.sent_start = False

        if self.recved_stopped == True:
            sde.entry_frames.delete(0, "end")
            sde.entry_frames.insert(0, "stopped(1)")
            return

        self.data = self.out_queue.dequeue()
        if self.data == "stopped" :
            self.recved_stopped == True
            sde.entry_frames.delete(0, "end")
            sde.entry_frames.insert(0, "stopped(2)")
            return
        
        x = 0
        while self.recved_stopped == False:
            time.sleep(0.5)
            x = self.out_queue.size()
            if x == 0:
                continue

            self.data = self.out_queue.dequeue()
            if self.data == "stopped" :
                self.recved_stopped = True
                sde.entry_frames.delete(0, "end")
                sde.entry_frames.insert(0, "stopped")
                break


if __name__ == "__main__":

    # set select_rect here if one needs a pre-selected area for video
    select_rect = rectx(967, 388, 1195, 481)
    fps = 17

    app = App()
    app.mainloop()

"""
https://github.com/blewett/Capture-on-Screen-Demos/tree/main
capture_demos.py: Original work Copyright (C) 2025 by Blewett

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Softxware, and to permit persons to whom the Software is
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
import threading
import pyaudio
import wave
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import time
import cv2

from PIL import ImageGrab
from PIL import Image
import numpy as np
import os
import signal
import sys

# globals for the sweeping selection and updating fields
global canvas
global select_rect
global offset
global sre
global fps

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
        self.normalize_rect()
        self.x1 += x
        self.x2 += x
        self.y1 += y
        self.y2 += y
        self.calc_width()

    def calc_width(self):
        self.normalize_rect()
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

select_rect = rectx(20,20,320,320)
offset = offsetPt(0,0)

global timer_entry_field
global frames_entry_field
global fps_entry_field
global timer_start_time

"""
should one want to do this in a function rather than inline

def timer_task():
    global timer_start_time
    global timer_entry_field

    elapsed = str(int(time.time() - timer_start_time))

    try:
        timer_entry_field.delete(0, "end")
        timer_entry_field.insert(0, elapsed)
    except:
        pass
"""

class RepeatingTimerThread(threading.Thread):
    def __init__(self, interval, function, *args, **kwargs):
    #def __init__(self, interval, function):
        super().__init__()
        self.interval = interval
        #self.function = function
     
        self.args = args
        self.kwargs = kwargs
     
        self.stop_event = threading.Event()
        self.running = False


    def run(self):
        # print("[timer] started...")
        global timer_start_time
        global timer_entry_field

        self.running = True

        timer_start_time = time.time()

        while not self.stop_event.is_set():
            # self.function(*self.args, **self.kwargs)
            if self.running == False:
                break

            elapsed = str(int(time.time() - timer_start_time))
            # print("elapsed = " + elapsed)
            try:
                timer_entry_field.delete(0, "end")
                timer_entry_field.insert(0, elapsed)
            except:
                pass

            self.stop_event.wait(self.interval)


    def stop(self):
        self.running = False
        self.stop_event.set()


class AudioRecordingThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []
        print()
        print("Ignore the following messages from audio selection")
        print()
        self.p = pyaudio.PyAudio()
        print()
        print("end of ignored messages from audio selection")
        print()

        self.stream = None
        self.running = False

    def load(self, string_name):
        self.string_name = string_name
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)

    def run(self):
        # print("[audio] Recording started...")
        self.running = True

        while self.running:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # Save audio to WAV
        output_filename = "audio" + self.string_name + ".wav"
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        # print(f"[audio] Recording saved to {self.output_filename}")

    def stop(self):
        self.running = False

# selecting rectangles from the screen - data and code
def start_drawing(event):
    global select_rect

    select_rect.x1 = event.x
    select_rect.y1 = event.y

def draw_rectangle(event):
    global canvas
    global select_rect

    canvas.delete("rectangle")
    canvas.create_rectangle(select_rect.x1, select_rect.y1,
                            event.x, event.y, tags="rectangle", width=4)

def end_drawing(event):
    global canvas
    global select_rect
    global sre

    select_rect.x2 = event.x
    select_rect.y2 = event.y
    select_rect.calc_width()

    canvas.create_rectangle(select_rect.x1, select_rect.y1,
                            select_rect.x2, select_rect.y2,
                            tags="rectangle")

    offset = offsetPt(canvas.winfo_rootx(), canvas.winfo_rooty())

    select_rect.addoffset(offset.x, offset.y)
    select_rect.normalize_rect()

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

    toplevel.title("Select an Area and then close the window")
    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    canvas_width = int (round (screen_width * 0.99))
    canvas_height = int (round (screen_height * 0.99))

    canvas = tk.Canvas(toplevel, width=canvas_width, height=canvas_height)
    canvas.pack()

    canvas.bind("<Button-1>", start_drawing)
    canvas.bind("<B1-Motion>", draw_rectangle)
    canvas.bind("<ButtonRelease-1>", end_drawing)

    # alpha has to be set after visibility
    toplevel.wait_visibility(toplevel)
    toplevel.wm_attributes('-alpha', 0.5)

    return canvas


class Select_video_area:
    def __init__(self, toplevel, set_rectx_button):

        global canvas
        global select_rect

        self.set_rectx_button = set_rectx_button
        self.toplevel = toplevel

        canvas = create_canvas(toplevel)
        canvas.pack(expand=True)

        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()

        canvas_width = int (round (screen_width * 0.99))
        canvas_height = int (round (screen_height * 0.99))

        close_button = tk.Button(canvas, bg="red", text="Close",
                                 command=self.canvas_close)
        close_button.place(x=(canvas_width / 2), y=0)

        """
        # center if toplevel is less than full screen
        x = int (round (screen_width - canvas_width) / 2)
        y = int (round (screen_height - canvas_height) / 2)
        toplevel.geometry(str(canvas_width) + "x" + str(canvas_height) +
                          "+" + str(x) + "+" + str(y))
        """

    def canvas_close(self):
        self.toplevel.withdraw()
        canvas.destroy()
        self.toplevel.destroy()
        self.set_rectx_button.config(state=tk.NORMAL)


# end of selecting rectangles from the screen

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


def validate_test_value(new_value):
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
    if validate_test_value(new_value) == False:
        return False
    select_rect.x1 = int(new_value)
    return True

def validate_select_entry_y1(new_value):
    global select_rect

    if new_value == "":
        return True
    if validate_test_value(new_value) == False:
        return False
    select_rect.y1 = int(new_value)
    return True

def validate_select_entry_x2(new_value):
    global select_rect

    if new_value == "":
        return True
    if validate_test_value(new_value) == False:
        return False
    select_rect.x2 = int(new_value)
    return True

def validate_select_entry_y2(new_value):
    global select_rect

    if new_value == "":
        return True
    if validate_test_value(new_value) == False:
        return False
    select_rect.y2 = int(new_value)
    return True

def validate_fps_entry(new_value):
    global fps

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


# VideoRecordingThread class - writes video captured from the screen for demos
class VideoRecordingThread(threading.Thread):
    def __init__(self, select_rect):
        super().__init__()
        global fps

        self.select_rect = select_rect
        self.running = True


    def load(self, string_name):
        self.string_name = string_name

        check_select_rect()

        recording_filename = time.strftime("video" + string_name + ".avi")

        #.mp4 = codec id 2
        #fourcc = cv2.VideoWriter_fourcc(*'I420') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'MP4V') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'MP42') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'AVC1') # error libx264
        #fourcc = cv2.VideoWriter_fourcc(*'H264') # error libx264
        #fourcc = cv2.VideoWriter_fourcc(*'WRAW') # error --- no information ---
        #fourcc = cv2.VideoWriter_fourcc(*'MPEG') # .avi 30fps
        #fourcc = cv2.VideoWriter_fourcc(*'MJPG') # .avi
        fourcc = cv2.VideoWriter_fourcc(*'XVID') # .avi
        #fourcc = cv2.VideoWriter_fourcc(*'H265') # error 

        #
        # collect and write the video
        #
        self.recording_writer = cv2.VideoWriter(recording_filename, fourcc, fps,
                                           (select_rect.width, select_rect.height))
        frames_entry_field.delete(0, "end")

    # writer loop
    def run(self):
        global frames_entry_field
        global fps_entry_field

        self.running = True
        num_frames_read = 0
        timer_start_time = time.time()

        while self.running:
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

        # calculate FPS
        end = time.time()
        #seconds = round(end - timer_start_time) & (~1)
        seconds = round(end - timer_start_time)
        fps = 0
        if seconds > 0:
            # fps = round(num_frames_read / seconds) & (~1)
            fps = round(num_frames_read / seconds)

        """
        print()
        print("approx. running time: " + str(seconds))
        print("approx. frames writen per second: " + str(fps))
        print("num_frames_read = " + str(num_frames_read))
        """

        frames_entry_field.delete(0, "end")
        frames_entry_field.insert(0, str(num_frames_read))

        fps_entry_field.delete(0, "end")
        fps_entry_field.insert(0, str(fps))


    def stop(self):
        self.running = False

# end of VideoRecordingThread class

class DataEntries():
    def __init__(self, data_frame):

        global timer_entry_field
        global frames_entry_field
        global fps_entry_field

        self.data_frame = data_frame

        #
        # time
        self.label_time = ttk.Label(self.data_frame, text="approx. time:")
        self.label_time.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.timer_entry_field = ttk.Entry(self.data_frame, width=10)
        self.timer_entry_field.grid(row=0, column=1, padx=5, pady=5, ipadx=5, sticky='w')
        timer_entry_field = self.timer_entry_field        

        #
        # frames
        self.label_frames = ttk.Label(self.data_frame, text="frame count:")
        self.label_frames.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        
        self.frames_entry_field = ttk.Entry(self.data_frame, width=10)
        self.frames_entry_field.grid(row=1, column=1, padx=5, pady=5, ipadx=5, sticky='w')
        frames_entry_field = self.frames_entry_field


class SelectRectEntries():
    def __init__(self, frame):
        global fps_entry_field

        self.frame = frame

        validate_select_x1 = frame.register(validate_select_entry_x1)
        validate_select_y1 = frame.register(validate_select_entry_y1)
        validate_select_x2 = frame.register(validate_select_entry_x2)
        validate_select_y2 = frame.register(validate_select_entry_y2)
        validate_fps = frame.register(validate_fps_entry)

        ttk.Label(frame, text="selection rectangle = ").grid(row=1, column=0,
                                                             padx=5, pady=5,
                                                             sticky="e")

        index = 1
        self.entry_x1 = ttk.Entry(frame, width=4, validate='key',
                                  validatecommand=(validate_select_x1, '%P'))
        self.entry_x1.grid(row=1, column=index, padx=5, pady=5)

        index += 1
        self.entry_y1 = ttk.Entry(frame, width=4, validate='key',
                                  validatecommand=(validate_select_y1, '%P'))
        self.entry_y1.grid(row=1, column=index, padx=5, pady=5)

        index += 1
        self.entry_x2 = ttk.Entry(frame, width=4, validate='key',
                                  validatecommand=(validate_select_x2, '%P'))
        self.entry_x2.grid(row=1, column=index, padx=5, pady=5)

        index += 1
        self.entry_y2 = ttk.Entry(frame, width=4, validate='key',
                                  validatecommand=(validate_select_y2, '%P'))
        self.entry_y2.grid(row=1, column=index, padx=5, pady=5)


        ttk.Label(frame, text="frames per second = ").grid(row=3, column=0,
                                                           padx=5, pady=5,
                                                           sticky="e")

        self.fps_entry_field = ttk.Entry(frame, width=2, validate='key',
                                    validatecommand=(validate_fps, '%P'))
        self.fps_entry_field.grid(row=3, column=1)
        fps_entry_field = self.fps_entry_field


class CaptureApp(tk.Tk):
    def __init__(self):
        super().__init__()

        global sre
        global sde
        global fps

        self.title("Capture on Screen Demos")
        self.running = False

        self.data_frame = ttk.LabelFrame(self)

        self.data_frame.grid(row=0, column=1, padx=5, pady=5)
        sde = DataEntries(self.data_frame)
        
        sde.timer_entry_field.delete(0, "end")
        sde.timer_entry_field.insert(0, "0")

        sde.frames_entry_field.delete(0, "end")
        sde.frames_entry_field.insert(0, "0")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=5, columns=2, padx=55, pady=20, sticky='ew')

        self.record_frame = ttk.Frame(self)
        self.record_frame.grid(row=6, column=1, padx=5, pady=5)

        self.start_button = ttk.Button(self.record_frame, text="Start",
                                       command=self.start_recording)
        self.start_button.grid(row=0, columns=2, padx=5, pady=5, sticky='ew')

        self.stop_button = ttk.Button(self.record_frame, text="Stop",
                                      command=self.stop_recording,
                                      state=tk.DISABLED)

        self.stop_button.grid(row=1, columns=2, padx=5, pady=5, sticky='ew')

        self.record_audio = tk.IntVar(value=0)
        self.checkbox_record_audio = ttk.Checkbutton(self.record_frame,
                                                     text="record audio",
                                                     variable=self.record_audio)

        self.checkbox_record_audio.grid(row=2, column=1, padx=5, pady=5,
                                        sticky='ew')

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=10, columns=2, padx=55, pady=20, sticky='ew')

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

        sre.fps_entry_field.delete(0, "end")
        sre.fps_entry_field.insert(0, str(fps))

        self.set_rectx_button = ttk.Button(self, text='sweep out area to be captured',
                                           command=self.set_select_rect)

        self.set_rectx_button.grid(row=12, columns=5, padx=5, pady=5)

        self.video_thread = None
        self.audio_thread = None
        self.string_name = "some string"


    def start_recording(self):
        if self.video_thread and self.video_thread.is_alive():
            print("[video]", "Already recording!")
            return

        """
        if self.audio_thread and self.audio_thread.is_alive():
            print("[audio]", "Already recording!")
            return
        """
        #
        # Create a timer that calls my_function every 1 second
        #
        #self.timer = RepeatingTimerThread(1, timer_task)
        self.timer_thread = RepeatingTimerThread(1, None)

        self.string_name = time.strftime("-%d-%m-%Y-%H-%M-%S")

        self.video_thread = VideoRecordingThread(select_rect)
        self.video_thread.load(self.string_name)

        if (self.record_audio.get()):
            self.audio_thread = AudioRecordingThread()
            self.audio_thread.load(self.string_name)

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        self.timer_thread.start()

        if (self.record_audio.get()):
            self.audio_thread.start()

        self.video_thread.start()


    def stop_recording(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.timer_thread.stop()
        self.video_thread.stop()
        if (self.record_audio.get()):
            self.audio_thread.stop()

    def set_select_rect(self):
        global select_rect

        self.set_rectx_button.config(state=tk.DISABLED)
        check_select_rect()
        toplevel = tk.Toplevel(self)
        # Optional: Remove window decorations
        #toplevel.overrideredirect(True)
        Select_video_area(toplevel, self.set_rectx_button)


# this is useful if the user exits while the system is capturing video
def on_closing():
    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == "__main__":

    # set select_rect here if one needs a pre-selected area for video
    select_rect = rectx(20, 20, 320, 320)
    fps = 20

    app = CaptureApp()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

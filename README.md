# Python3 Tkinter program "Capture on Screen Demos"
 The python3 program included here is used for producing videos from on screen demo displays.

![capture-demos](https://github.com/user-attachments/assets/88ed8852-8102-4905-a47b-b9a02de1d5bf)

This is a very simple system for capturing on screen activities.  This program does not capture audio.  Better video demos add the audio after the demo video has been created.  One might use a program like "audacity" to narrate demos.  Capture the narration while playing the video - always a better result than driving and talking.  Add the audio using a program like "openshot".

![capture-demos-sweep](https://github.com/user-attachments/assets/fd1f0e4d-5c94-417a-8453-9ca748bf9711)

The program, capture.demos.py, pops up a window to allow the user to sweep out arbitrary areas of the computer screen for recording.  Do this by pressing the "sweep out area to be captured" button.  The area to be recorded may also be set using the on program screen coordinates in the "selection rectangle" text boxes or by adding the rectangle to the bottom of capture.demos.py.  One can start and stop the recording as needed.

This system is built on the Open Computer Vision module (cv2) and the  tkinter GUI package. Install these, after installing python3, with the following:

1. pip3 install opencv-python
2. sudo apt-get install python3-tk
3. pip3 install --upgrade Pillow

The following is a sample invocation of the system:

 python3 capture_demos.py

I hope this helps.  You are on your own – but you already knew that.

Doug Blewett

doug.blewett@gmail.com

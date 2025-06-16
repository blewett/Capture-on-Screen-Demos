# Tkinter Capture-on-Screen-Demos
 Capture on Screen Demos is used for producing videos from on screen demo displays.

![alt text](https://github.com/blewett/capture_demos/blob/capture-demos.png/?raw=true)

This is a simple system for capturing on screen activities.  This is used for producing videos from on screen demo displays.

This does not capture audio.  Better video demos add the audio after the demo has been created.  One might use a program like "audacity" to narrate demos.  Capture the narration while playing the video - always a better result than driving and talking.  Add the audio using a program like "openshot".

![alt text](https://github.com/blewett/capture_demos/blob/capture-demos-sweep.png/?raw=true)

capture.demos.py pops up a window to allow the user to sweep out arbitrary areas of the computer screen for recording.  The area to be recorded may be set using the on program screen coordinates or by adding those to the bottom of capture.demos.py.  One can start and stop the recording as needed.

This system is built on the Open Computer Vision module (cv2) and the  tkinter GUI package. Install these, after installing python3, with the following:

1. pip3 install opencv-python
2. sudo apt-get install python3-tk
3. pip3 install --upgrade Pillow

The following is a sample invocation of the system:

python3 capture_demos.py

I hope this helps.  You are on your own – but you already knew that.

Doug Blewett

doug.blewett@gmail.com

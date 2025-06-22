# Python3 Tkinter program "Capture on Screen Demos"
 The python3 program included here is used for producing videos from on screen demo displays.

![capture-demos](https://github.com/user-attachments/assets/88ed8852-8102-4905-a47b-b9a02de1d5bf)

This is a very simple system for capturing on computer screen demos.  It is entirely written in python and has a GUI interface.  All of that  can be modified it to do whatever one wants - easy.

This program does not capture audio.  Better video demos add the audio  after the demo video has been created and peiced together.  One might  use a program like "audacity" or "gnome recorder" to capture narrative  for the demo.  One can capture the narration while playing the  captured video.  The results are always a better than driving and  talking.  Add the audio recording using a program like "openshot" or  "ffmpeg".  Openshot is also good for combing multiple videos - common.

![demos-start](https://github.com/user-attachments/assets/9d0a8ddb-6404-4eb2-8941-46a135e6b431)

A few words about "openshot": openshot has limits on image size.  We  are not sure why that is true.  Use the advanced setting and multipy  width and height by some percentage to reduce the size of your video  images.  To reduce final video file size reduce the frames per second  and/or the bit rate / quality to values less than 15 Mbs.  File sizes  of video produced by the "capture demo" program are quite small in  most cases.

https://github.com/user-attachments/assets/a45355b2-f636-4033-952f-c1c8af96463f

The program, capture.demos.py, pops up a window to allow the user to  sweep out arbitrary areas of the computer screen for recording.  Do  this by pressing the "sweep out area to be captured" button.  The area  to be recorded may also be set using the on program screen coordinates  in the "selection rectangle" text boxes or by adding the selection  rectangle to the bottom of capture_demos.py.  One can start and stop  the recording as needed.

This system is built on the Open Computer Vision module (cv2) and the  tkinter GUI package. Install these, after installing python3, with the following:

1. pip3 install opencv-python
2. sudo apt-get install python3-tk
3. pip3 install --upgrade Pillow

The following is a sample invocation of the system:

 python3 capture_demos.py

I hope this helps.  You are on your own – but you already knew that.

Doug Blewett

doug.blewett@gmail.com

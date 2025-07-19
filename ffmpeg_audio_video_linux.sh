#
#  Merge an audio file with a video file using
#  FFmpeg's audio and video mapping features.
#  This script use ffmpeg and ffprobe.  The
#  ratio of the video to the audio file is
#  used to adjust the video and audio files
#  to equal lengths.
#
#     sudo apt install ffmpeg
#
#  Doug Blewett July 2025
#
if [ $# -ne 2 ]; then
    echo "The number of arguments entered was $#.  Two arguments are required."
    echo "The arguments are video file name and the audio file name."
    echo
    echo "You entered: \"$@\""
    echo
    echo "Correct syntax:    $0 video-file auto-file"
    echo
    exit 1
fi

#
# get the length of the video file and the audio file
#
len_video=`ffprobe -i $1 -show_entries format=duration -v quiet -of csv="p=0"`

len_audio=`ffprobe -v error -select_streams a:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 $2`

echo "len_audio = $len_audio"
echo "len_video = $len_video"
output_file=x`echo $1 | sed -e "s/\..*$//"`.mp4
echo "output_file: $output_file"

#
# determine the size ratio of the video file to the audio file
#
ratio=`echo "scale=4; $len_video / $len_audio" | bc`
echo "ratio = $ratio"

#
# make the video file the same length as the audio file
#
ffmpeg -i $1 -vf "setpts=PTS/$ratio" x.mp4

#
# combine the video file and the audio file
#
ffmpeg -hide_banner -i x.mp4 -i $2 \
       -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 \
       $output_file
rm -f x.mp4

echo "ratio = $ratio"

exit

#
# offset technique
#
# offset=`echo $offset | sed -e "s/^\./0./"`
# echo "offset: $offset"
# 
# ffmpeg -hide_banner -itsoffset "$offset" -i $1 -i $2 \
#        -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 \
#        $output_file
# 

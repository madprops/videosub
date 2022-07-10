Send it a video path and a path of a text file with some lines.

It will generate the subtitles .srt file.

Each line will add a bit to the duration depending on its length.

The shortest line is at least 1 second long.

It will then create a slice of the video.

Then add the subtitles to the slice.

Temporary files are stored in /table

The output videos are saved in /output.

ffmpeg needs to be installed.
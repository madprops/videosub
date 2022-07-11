# Hint: use fc-scan to get the fullname of font files

import os
import sys
import random
import math
import time
from pathlib import Path
from subprocess import check_output
from datetime import datetime, timedelta

# Path where there script is
dirname: str

# Seconds used between subtitle items
sub_gap = 0.5

# Higher = Longer subtitle item duration
sub_weight = 0.088

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# To srt timestamp format
def srt_timestamp(td) -> str:
  hrs, secs_remainder = divmod(td.seconds, 3600)
  hrs += td.days * 24
  mins, secs = divmod(secs_remainder, 60)
  msecs = td.microseconds // 1000
  return "%02d:%02d:%02d,%03d" % (hrs, mins, secs, msecs)

# Get subtitles duration
def get_sub_duration(lines) -> int:
  seconds = sub_gap
  
  for i, line in enumerate(lines):
    seconds += max(len(line) * sub_weight, 1) 
    if i < len(lines) - 1:
      seconds += sub_gap       

  return int(math.ceil(seconds))  

# Create the srt subtitles file
def make_subtitles(lines, start) -> None:
  # Starting seconds
  seconds = start + sub_gap

  items = []
  subs = []

  for i, line in enumerate(lines):
    text = f"{i + 1}\n"

    # Line duration based on char length
    line_duration = max(len(line) * sub_weight, 1)

    # Start and end timestamps
    text += srt_timestamp(timedelta(seconds=seconds))
    text += " --> "
    text += srt_timestamp(timedelta(seconds=seconds + line_duration))
    
    # Text content
    text += f"\n{line}"

    # Add to list to join later
    items.append(text)
    
    # Increase seconds used
    seconds += line_duration
    
    # Add a gap between lines
    # Unless it's the last item
    if i < len(lines) - 1:
      seconds += sub_gap
  
  # Save srt file to table
  f = open(f"{dirname}/table/subtitles.srt", "w")
  f.write("\n".join(items))
  f.close()

# Get video duration
def get_video_duration(path: str) -> int:
  d = check_output(['ffprobe', '-i', path, '-show_entries', \
  'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")])
  d = d.decode("utf-8").strip()
  return int(float(d))  

# Main function
def main() -> None:
  global dirname

  if len(sys.argv) < 3:
    return

  # Arguments
  video_path = sys.argv[1]
  text_path = sys.argv[2]

  dirname = clean_path(os.path.dirname(os.path.realpath(__file__)))

  if not Path(video_path).exists():
    print("Invalid video path.")
    exit(1)

  if not Path(text_path).exists():
    print("Invalid text path.")
    exit(1)
  
  # To calculate performance
  time_start = time.time()

  # Subtitle input lines
  sub_lines = open(text_path, "r").readlines()

  # Check original video duration
  max_duration = get_video_duration(video_path)

  # Get subtitles duration
  duration = get_sub_duration(sub_lines)

  if duration >= max_duration:
    print("Video is too short.")
    exit(1)

  if len(sys.argv) > 3:
    # If start seconds supplied
    start = int(sys.argv[3])
    if start + duration >= max_duration:
      print("Start position has to be shorter.")
      exit(1)
  else:
    # Get a random start seconds
    start = random.randint(0, max(0, max_duration - duration - 1))

  # Generate subtitles
  make_subtitles(sub_lines, start)    

  print(f"Start: {start} seconds")
  print(f"Duration: {duration} seconds")

  # Get file extension
  ext = Path(video_path).suffix
  
  # Unix seconds
  now = int(datetime.now().timestamp())

  # Get the output name
  name = "".join(filter(str.isalnum, Path(video_path).stem))[0:10] or "output"

  # Subtitles style
  style = f"force_style='BackColour=&H80000000,BorderStyle=4,Fontsize=16,FontName=Roboto'"
  
  # Start of ffmpeg command
  ffmpeg_cmd = "ffmpeg -hide_banner -loglevel error -y"

  # Mix clip with subtitles
  os.popen(f"{ffmpeg_cmd} -i '{video_path}' -filter_complex \
  \"subtitles={dirname}/table/subtitles.srt:fontsdir={dirname}/fonts:{style}\" \
  -ss {start} -t {duration} {dirname}/output/{name}_{now}{ext}").read() 
  
  # End message
  time_end = time.time()
  diff = int(time_end - time_start)
  print(f"Done in {diff} seconds")
  
# Program starts here
if __name__ == "__main__": main()
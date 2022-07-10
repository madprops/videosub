# Hint: use fc-scan to get the fullname of font files

import os
import sys
import subprocess
import random
import math
import time
from pathlib import Path
from datetime import datetime, timedelta

# Path where there script is
dirname: str

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# To srt timestamp format
def srt_timestamp(td):
  hrs, secs_remainder = divmod(td.seconds, 3600)
  hrs += td.days * 24
  mins, secs = divmod(secs_remainder, 60)
  msecs = td.microseconds // 1000
  return "%02d:%02d:%02d,%03d" % (hrs, mins, secs, msecs)

# Create the srt subtitles file
def make_srt(text_path: str) -> int:
  lines = open(text_path, "r").readlines()

  # Seconds used between subtitle items
  gap = 0.5

  # Higher = Longer item duration
  weight = 0.088

  seconds = gap
  items = []
  subs = []

  for i, line in enumerate(lines):
    text = f"{i + 1}\n"

    # Line duration based on char length
    line_duration = max(len(line) * weight, 1)

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
      seconds += gap
  
  # Save srt file to table
  f = open(f"{dirname}/table/subtitles.srt", "w")
  f.write("\n".join(items))
  f.close()

  return int(math.ceil(seconds))

# Get video duration
def get_duration(path: str) -> int:
  d = subprocess.check_output(['ffprobe', '-i', path, '-show_entries', \
  'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")])
  d = d.decode("utf-8").strip()
  return int(float(d))  

# Main function
def main() -> None:
  global dirname

  if len(sys.argv) != 3:
    return

  # Arguments
  video_path = sys.argv[1]
  text_path = sys.argv[2]

  dirname = clean_path(os.path.dirname(os.path.realpath(__file__)))

  if not os.path.exists(video_path):
    print("Invalid video path.")
    exit(1)

  if not os.path.exists(text_path):
    print("Invalid text path.")
    exit(1)
  
  time_start = time.time()

  # Generate subtitles
  # And get their duration
  duration = make_srt(text_path)

  # Check original video duration
  max_duration = get_duration(video_path)

  # Get a random start position
  start = random.randint(0, max(0, max_duration - 1))

  # Get file extension
  ext = Path(video_path).suffix
  
  # Create slice from original video
  os.popen(f"ffmpeg -y -stream_loop -1 -ss {start} -t {duration} -i '{video_path}' -c copy {dirname}/table/clip{ext}").read()
  
  # Unix seconds
  now = int(datetime.now().timestamp())

  # Get the output name
  name = "".join(filter(str.isalnum, Path(video_path).stem))[0:10] or "output"

  # Subtitles style
  style = f"force_style='BackColour=&H80000000,BorderStyle=4,Fontsize=16,FontName=Roboto'"
  
  # Mix clip with subtitles
  os.popen(f"ffmpeg -y -i {dirname}/table/clip{ext} -filter_complex \
  \"subtitles={dirname}/table/subtitles.srt:fontsdir={dirname}/fonts:{style}\" \
  -ss 0 -t {duration} {dirname}/output/{name}_{now}{ext}").read() 
  
  time_end = time.time()
  diff = int(time_end - time_start)
  print(f"\nDone in {diff} seconds.")
  
# Program starts here
if __name__ == "__main__": main()
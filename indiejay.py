# pip install srt
# Hint: use fc-scan to get the fullname of font files

import os
import sys
import subprocess
import random
import math
import time
from srt import Subtitle, compose
from pathlib import Path
from datetime import datetime, timedelta

# Path where there script is
dirname: str

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Create the srt subtitles file
def make_srt(text_path: str) -> int:
  lines = open(text_path, "r").readlines()
  seconds = 0.5
  text = ""
  subs = []

  for i, line in enumerate(lines):
    # Line duration based on char length
    line_duration = max(len(line) * 0.08, 1)

    # Generate using srt library
    start = timedelta(seconds=seconds)
    end = timedelta(seconds=seconds + line_duration)
    
    # Create a subtitle item using the srt library
    subs.append(Subtitle(index=i + 1, start=start, end=end, content=line))
    
    # Increase seconds used
    seconds += line_duration
    # Add a gap between lines
    if i < len(lines) - 1:
      seconds += 0.5
  
  # Save srt file to table
  f = open(f"{dirname}/table/subtitles.srt", "w")
  f.write(compose(subs))
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
  start = random.randint(0, max_duration)

  # Get file extension
  ext = Path(video_path).suffix
  
  # Create slice from original video
  os.popen(f"ffmpeg -y -stream_loop -1 -ss {start} -t {duration} -i '{video_path}' -c copy {dirname}/table/clip{ext}").read()
  
  # Unix seconds
  now = int(datetime.now().timestamp())

  # Subtitles style
  style = f"force_style='BackColour=&H80000000,BorderStyle=4,Fontsize=16,FontName=Roboto'"
  
  # Mix clip with subtitles
  os.popen(f"ffmpeg -y -i {dirname}/table/clip{ext} -filter_complex \
  \"subtitles={dirname}/table/subtitles.srt:fontsdir={dirname}/fonts:{style}\" \
  -ss 0 -t {duration} {dirname}/output/out_{now}{ext}").read() 
  
  time_end = time.time()
  diff = int(time_end - time_start)
  print(f"\nDone in {diff} seconds.")
  
# Program starts here
if __name__ == "__main__": main()
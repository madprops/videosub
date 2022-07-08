import os
import sys
import subprocess
import random
import math
from srt import Subtitle, compose
from pathlib import Path
from datetime import datetime, timedelta

# Create the srt subtitles file
def make_srt(text_path: str) -> int:
  lines = open(text_path, "r").readlines()
  seconds = 0
  text = ""
  subs = []

  for i, line in enumerate(lines):
    # Line duration based on char length
    line_duration = max(len(line) * 0.1, 1)

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
  f = open("table/subtitles.srt", "w")
  f.write(compose(subs))
  f.close()

  return int(math.ceil(seconds))

# Get video duration
def get_duration(path: str) -> int:
  d = subprocess.check_output(['ffprobe', '-i', path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")])
  d = d.decode("utf-8").strip()
  return int(float(d))  

# Main function
def main() -> None:
  if len(sys.argv) != 3:
    return

  # Arguments
  video_path = sys.argv[1]
  text_path = sys.argv[2]

  if not os.path.exists(video_path):
    print("Invalid video path.")
    exit(1)

  if not os.path.exists(text_path):
    print("Invalid text path.")
    exit(1)

  # Generate subtitles
  # And get their duration
  duration = make_srt(text_path)

  # Check original video duration
  max_duration = get_duration(video_path)

  if max_duration < duration:
    print("Video is too short.")
    exit(1)

  # Get a random start position
  start = random.randint(0, max_duration - duration)
  ext = Path(video_path).suffix
  
  # Create slice from original video
  os.popen(f"ffmpeg -y -ss {start} -t {duration} -i {video_path} -c copy table/clip{ext}").read()
  
  # Unix seconds
  now = int(datetime.now().timestamp())

  # Subtitles style
  style = "force_style='BackColour=&H80000000,BorderStyle=4,Fontsize=14'"
  
  # Mix clip with subtitles
  os.popen(f"ffmpeg -y -i table/clip{ext} -filter_complex \"subtitles=table/subtitles.srt:{style}\" -ss 0 -t {duration} table/out_{now}{ext}").read() 
  print("Done.")
  
# Program starts here
if __name__ == "__main__": main()
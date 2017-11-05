#!/usr/bin/python3
import os
import sys

src = os.getcwd()+"/../src"
sys.path.insert(0, src)


from YouTube import *

from pprint import pprint
import time

def print_progress(status):
    print(str(float(status)*100)+"%")

youtube = YouTube()

youtube.authorize()

response = youtube.upload_video(video_path = "test.avi",
        title="This is a video",
        description="This is the description",
        privacy="unlisted",
        progress_callback=print_progress)


youtube.upload_thumbnail(video_id=response['id'],image_path="test.jpg")
        

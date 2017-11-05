#!/usr/bin/python3
import os
import sys

src = os.getcwd()+"/../src"
sys.path.insert(0, src)

from YouTube import *

from pprint import pprint
import time
youtube = YouTube()

youtube.authorize()

pprint( youtube.get_usable_category_ids() )

import os
import json

#
# ENV
#

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# connect to websocket
# receive latest blocks
# store information in database


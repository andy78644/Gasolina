import os
from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab

#
# ENV
#

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#
# CELERY
#

celery_app = Celery('tasks', backend=os.environ.get('REDIS_URL'), broker=os.environ.get('CELERY_URL'), broker_connection_retry_on_startup=True)
logger = get_task_logger(__name__)
celery_app.conf.task_default_queue=os.environ.get('CELERY_QUEUE')

#
# DATABASE
#

import pymysql

#
# SUI
#

import json

@celery_app.task(name='sui')
def sui():
  # DB
  db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

  # get data from blockchain table and calculcate latest fee and store in db
  # ....

  db.close()
  return('Finished')

#
# AVALANCHE
#

import json

@celery_app.task(name='avalanche')
def avalanche():
  # DB
  db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

  # get data from blockchain table and calculcate latest fee and store in db
  # ....

  db.close()
  return('Finished')

#
# SCHEDULER
#

#@app.on_after_configure.connect
#def setup_periodic_tasks(sender, **kwargs):
#  sender.add_periodic_task(10.0, sui.s(), name='refresh sui - every 10 seconds')
#  sender.add_periodic_task(30.0, avalanche.s(), name='refresh avalanche - every 30 seconds')

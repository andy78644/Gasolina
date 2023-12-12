import os
from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from datetime import datetime


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

'''
CREATE TABLE IF NOT EXISTS `chain_fee` (
	`id` int(11) NOT NULL auto_increment,
  `chain` varchar(250)  NOT NULL default '',
	`slow_base` int(11) NOT NULL default '0',
	`avg_base` int(11)  NOT NULL default '0',
	`fast_base`  int(11) NOT NULL default '0',
  `slow_price` int(11) NOT NULL default '0',
	`avg_price` int(11)  NOT NULL default '0',
	`fast_price`  int(11) NOT NULL default '0',
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
	`updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	 PRIMARY KEY  (`id`)
);
'''
#
# SUI
#

import json

@celery_app.task(name='sui')
def sui():
  # DB
  db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)
  # Now is Get 1000 transactions or 200 checkpoint(bolcks)
  cursor = db.cursor()
  cursor.execute("SELECT * FROM `sui_transactions` ORDER BY `total_fee`")
  transactions = cursor.fetchall()
  transaction_count = len(transactions)
  slow_count = int(transaction_count/3)
  avg_count = int(transaction_count/2)
  fast_count = int(transaction_count/10*9)
  avg_base = 0
  slow_base = 0
  fast_base = 0
  curr_base = 0
  avg_price = 0
  slow_price = 0
  fast_price = 0
  curr_price = 0
  for index, transaction in enumerate(transactions):
    curr_base += transaction["gas_price"]
    curr_price += transaction["total_fee"]
    if(index == slow_count):
      slow_base = curr_base/(index+1)
      slow_price = curr_price/(index+1)
    if(index == avg_count):
      avg_base = curr_base/(index+1)
      avg_price= curr_price/(index+1)
    if(index == fast_count):
      fast_base = curr_base/(index+1)
      fast_price = curr_price/(index+1)

  # print(slow_base, "slow_price",slow_price)
  # print(avg_base, "avg_price",avg_price)
  # print(fast_base, "fast_price",fast_price)
  time_now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
  cursor.execute("INSERT INTO `chain_fee` ( \
				chain, \
				slow_base, \
				avg_base, \
				fast_base, \
        slow_price, \
				avg_price, \
				fast_price, \
        created_at, \
				updated_at \
				) VALUES ('%s', %d, %d, %d, %d, %d, %d, '%s', '%s') \
				" % ("sui", slow_base, avg_base, fast_base, slow_price, avg_price, fast_price, time_now,time_now))
      #print(cursor)
  db.commit()
  cursor.close()
  db.close()
  # get data from blockchain table and calculcate latest fee and store in db
  # ....
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

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
 sender.add_periodic_task(10.0, sui.s(), name='refresh sui - every 10 seconds')
#  sender.add_periodic_task(30.0, avalanche.s(), name='refresh avalanche - every 30 seconds')

import os
import sys
import json
import requests
from datetime import datetime
import statistics

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

from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab

celery_app = Celery('tasks', backend=os.environ.get('REDIS_URL'), broker=os.environ.get('CELERY_URL'), broker_connection_retry_on_startup=True)
logger = get_task_logger(__name__)
celery_app.conf.task_default_queue=os.environ.get('CELERY_QUEUE')

#
# DATABASE
#

import pymysql

'''
CREATE TABLE IF NOT EXISTS `bnb_calculation` (
	`id` int(11) NOT NULL auto_increment,
	`slow` bigint(11) NOT NULL default '0',
	`average` bigint(11) NOT NULL default '0',
	`fast`  bigint(10) NOT NULL default '0',
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
	`updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	 PRIMARY KEY  (`id`)
);
'''

@celery_app.task(name='processing')
def processing():
	# DB
	db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

	url = "https://bsc.publicnode.com"
	#url = "https://docs-demo.bsc.quiknode.pro/"

	payload = json.dumps({
		"method": "txpool_content",
		"params": [],
		"id": 1,
		"jsonrpc": "2.0"
	})
	headers = {
		'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=payload)
	pending_transactions = response.json()

	gas_prices = []
	for tx in pending_transactions["result"]["pending"[:10]]:
		for pending in pending_transactions["result"]["pending"][tx]:
			for name, value in pending_transactions["result"]["pending"][tx][pending].items():
				if name == 'gasPrice':
					gasprice = int(value, 16)
					gas_prices.append(gasprice)
					#print('found gas %s (%s)' % (value,gasprice))

	meanaverage = statistics.mean(gas_prices)
	slow = int(meanaverage) + 1000000000
	average = int(meanaverage) + 1000000000
	fast = int(meanaverage) + 1000000000

	print("calculated: %s" % (meanaverage))
	#print("median: ", statistics.median(gas_prices))

	print("slow: %s" % (slow))
	print("average: %s" % (average))
	print("fast: %s" % (fast))

	cursor = db.cursor()
	cursor.execute("INSERT INTO `bnb_calculation` ( \
		slow, \
		average, \
		fast \
		) VALUES ('%s','%s','%s') " % (slow,average,fast))
	db.commit()
	cursor.close()

	db.close()
	return('Finished')

#
# SCHEDULER
#

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
	sender.add_periodic_task(10.0, processing.s(), name='refresh data - every 10 seconds')

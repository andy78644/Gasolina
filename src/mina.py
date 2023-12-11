import os
import json
import requests

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
db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

'''
CREATE TABLE IF NOT EXISTS `mina_transactions` (
	`id` int(11) NOT NULL auto_increment,
	`block` int(11) NOT NULL default '0',
	`state` varchar(250)  NOT NULL default '',
	`fee`  int(11) NOT NULL,
	`type` varchar(10)  NOT NULL default '',
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
	`updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	 PRIMARY KEY  (`id`)
);
'''

@celery_app.task(name='processing')
def processing():
	# DB
	db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

	url = "https://api.minaexplorer.com/blocks"
	headers = {'Accept': 'application/json'}
	querystring = {"limit":1}

	response = requests.request("GET", url, headers=headers, params=querystring)

	data = response.json()
	blockHeight = data['blocks'][0]['blockHeight']
	snarkJobs = data['blocks'][0]['snarkJobs']
	userCommands = data['blocks'][0]['transactions']['userCommands']
	feeTransfer = data['blocks'][0]['transactions']['feeTransfer']

	print('latest block %s' % (blockHeight))

	# check if block is already processed
	cursor = db.cursor()
	cursor.execute("SELECT id FROM `mina_transactions` WHERE block='%s'" % (blockHeight))
	block_id = cursor.fetchone()

	if block_id:
		print('block already processed')

	else:
		# add snark transactions to database
		for snark in snarkJobs:
			print('found snark fee: %s state %s' % (snark['fee'],snark['blockStateHash']))

			time_now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

			cursor = db.cursor()
			cursor.execute("INSERT INTO `mina_transactions` ( \
				block, \
				state, \
				fee, \
				type, \
				created_at, \
				updated_at, \
				) VALUES ('%s','%s','%s','%s','%s','%s') \
				" % (int(blockHeight),snark['blockStateHash'],int(snark['fee']),'snark'),time_now,time_now)
			db.commit()
			cursor.close()

		# add user transactions to database
		for user in userCommands:
			print('found user fee: %s state %s' % (user['fee'],user['blockStateHash']))

			cursor = db.cursor()
			cursor.execute("INSERT INTO `mina_transactions` ( \
				block, \
				state, \
				fee, \
				type, \
				created_at, \
				updated_at, \
				) VALUES ('%s','%s','%s','%s','%s','%s') \
				" % (int(blockHeight),user['blockStateHash'],int(user['fee']),'user'),time_now,time_now)
			db.commit()
			cursor.close()

		# add fee transactions to database
		for fee in feeTransfer:
			print('found user fee: %s state %s' % (fee['fee'],fee['blockStateHash']))

			cursor = db.cursor()
			cursor.execute("INSERT INTO `mina_transactions` ( \
				block, \
				state, \
				fee, \
				type, \
				created_at, \
				updated_at, \
				) VALUES ('%s','%s','%s','%s','%s','%s') \
				" % (int(blockHeight),fee['blockStateHash'],int(fee['fee']),'user'),time_now,time_now)
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

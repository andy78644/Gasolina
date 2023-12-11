import os
import json
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
CREATE TABLE IF NOT EXISTS `sui_transactions` (
	`id` int(11) NOT NULL auto_increment,
	`checkpoint` int(11) NOT NULL default '0',
	`gas_price` int(11)  NOT NULL,
	`total_fee`  int(11) NOT NULL,
	`tips` int(11)  NOT NULL,
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
	`updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	 PRIMARY KEY  (`id`)
);
'''

# connect to websocket
# receive latest blocks
# store information in database


import requests
import json
@celery_app.task(name='processing')
def processing():
  headers = {"Accept": "*/*","Content-Type": "application/json"}
  sui_url = "https://fullnode.mainnet.sui.io/"

  db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

  # Get gas price of epoch
  data = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "suix_getReferenceGasPrice",
    "params": []
  }
  res = requests.post(url = sui_url, data = json.dumps(data), headers = headers)
  gas_price = res.json()["result"]

  # Get the latest checkpoint(blocks)
  data = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "sui_getLatestCheckpointSequenceNumber",
    "params": []
  }
  res = requests.post(url = sui_url, data = json.dumps(data), headers = headers)
  latest_checkpoint = res.json()["result"]
  print(latest_checkpoint)

  # check if block is already processed
  cursor = db.cursor()
  cursor.execute("SHOW TABLES")
  cursor.execute("SELECT id FROM `sui_transactions` WHERE checkpoint='%s'" % (latest_checkpoint))
  checkpoint_id = cursor.fetchone()

  if checkpoint_id:
    print('checkpoint already processed')

  else:
    # Get all transaction in latest checkpoint
    data = {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "sui_getCheckpoint",
      "params": [
        latest_checkpoint
      ]
    }
    res = requests.post(url = sui_url, data = json.dumps(data), headers = headers)
    transactions = res.json()["result"]["transactions"]

    # Get gas_price and gas fee user paid
    data = {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "sui_multiGetTransactionBlocks",
      "params": [
        transactions,
        {
          "showInput": True,
          "showRawInput": False,
          "showEffects": True,
          "showEvents": False,
          "showObjectChanges": False,
          "showBalanceChanges": False
        }
      ]
    }
    res = requests.post(url = sui_url, data = json.dumps(data), headers = headers)
    transactions = res.json()["result"]

    for transaction in transactions:
      # print(transaction["effects"]["gasUsed"])
      # print(transaction["transaction"]["data"]["gasData"]["price"])
      gas_used = transaction["effects"]["gasUsed"]
      total_fee = int(gas_used["computationCost"]) + int(gas_used["storageCost"]) + int(gas_used["storageRebate"])
      tips = int(transaction["transaction"]["data"]["gasData"]["price"]) - int(gas_price)
      time_now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
      cursor = db.cursor()
      cursor.execute("INSERT INTO `sui_transactions` ( \
				checkpoint, \
				gas_price, \
				total_fee, \
				tips, \
        created_at, \
				updated_at \
				) VALUES (%d,%d,%d,%d, '%s', '%s') \
				" % (int(latest_checkpoint), int(gas_price), int(total_fee), int(tips),time_now,time_now))
      db.commit()
      cursor.close()
  db.close()
  return('Finished')

# def main():
#   print("Hello World!")
#   store_sui_data()

# if __name__ == "__main__":
#   main()

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
	sender.add_periodic_task(10.0, processing.s(), name='refresh data - every 10 seconds')


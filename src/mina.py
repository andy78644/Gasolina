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
# DATABASE
#

import pymysql
db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

# connect to websocket
# receive latest blocks
# store information in database

def main():
	url = "https://api.minaexplorer.com/blocks"
	headers = {'Accept': 'application/json'}
	querystring = {"limit":1}

	response = requests.request("GET", url, headers=headers, params=querystring)

	data = response.json()
	blockHeight = data['blocks'][0]['blockHeight']
	snarkJobs = data['blocks'][0]['snarkJobs']

	print('block %s' % (blockHeight))

	# check if block is already processed
	cursor = db.cursor()
	cursor.execute("SELECT id FROM `mina_transactions` WHERE block='%s'" % (blockHeight))
	block_id = cursor.fetchone()

	if block_id:
		print('block already processed')

	else:

		# add transactions to database
		for snark in snarkJobs:
			print('found fee: %s state %s' % (snark['fee'],snark['blockStateHash']))

			cursor = db.cursor()
			cursor.execute("INSERT INTO `mina_transactions` ( \
				block, \
				state, \
				fee \
				) VALUES ('%s','%s','%s') \
				" % (int(blockHeight),snark['blockStateHash'],int(snark['fee'])))
			db.commit()
			cursor.close()

if __name__ == "__main__":
	main()


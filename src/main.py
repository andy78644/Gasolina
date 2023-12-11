import os
import json
from fastapi import Depends, FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from enum import Enum

#
# ENV
#

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#
# FASTAPI
#

app = FastAPI(
  title="API",
  description="Fee Estimations Predictions",
  version="1.0",
)

#
# CELERY
#

from celery import Celery
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
celery_app = Celery( "tasks", backend=os.environ.get('REDIS_URL'), broker=os.environ.get('CELERY_URL'), broker_connection_retry_on_startup=True)
celery_app.conf.task_default_queue=os.environ.get('CELERY_QUEUE')

#
# DATABASE
#

import pymysql
db = pymysql.connect(host=os.environ.get('DATABASE_HOST'),user=os.environ.get('DATABASE_USER'),password=os.environ.get('DATABASE_PASSWORD'),database=os.environ.get('DATABASE_DB'),cursorclass=pymysql.cursors.DictCursor)

#
# API
#

class BlockchainName(str, Enum):
  sui = "sui"
  avalanche = "avalanche"
  bnb = "bnb"
  mina = "mina"

class SpeedName(str, Enum):
  slow = "slow"
  medium = "medium"
  fast = "fast"

@app.get("/api/v1/gas/{blockchain}", tags=["gas"])
async def gas(
  blockchain: BlockchainName
  ):
  # todo query db and respond last fee estimation
  return blockchain

@app.get("/api/v1/gas/{blockchain}/{speed}", tags=["gas"])
async def gas_by_speed(
  blockchain: BlockchainName,
  speed: SpeedName
  ):
  # todo query db and respond last fee estimation
  return blockchain


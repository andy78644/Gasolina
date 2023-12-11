#!/bin/bash
# script: run command in container

APP=$1

echo "starting application"
cd /app/
if [ $APP == 'api' ]; then
  uvicorn src.main:app --host 0.0.0.0 --log-level info --reload

elif [ $APP == 'scheduler' ]; then
  cd /app/src/
  rm celerybeat-schedule 2>/dev/null
  export CELERY_QUEUE=scheduler
  celery -A $APP worker -B --loglevel=info -Q $CELERY_QUEUE -P prefork --concurrency=1 -s celerybeat-$APP

else
  print "something is wrong... oh lala"
fi

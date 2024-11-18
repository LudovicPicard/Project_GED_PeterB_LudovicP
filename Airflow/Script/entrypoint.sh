#!/bin/bash
set -e   #script exit immediately if any command fails
 
if [ -e "/opt/airflow/requirements.txt" ]; then
  $(command python) pip install --upgrade pip
  $(command -v pip) install --user -r requirements.txt
fi
 
if [ ! -f "/opt/airflow/airflow.db" ]; then
  airflow db init && \
  airflow users create \
    --username LudovicPicard \
    --firstname Ludovic \
    --lastname Picard \
    --role Admin \
    --email ludovic.picard@supdevinci-edu.fr \
    --password z2VVv6M9QrTxCrxK
fi
 
$(command -v airflow) db upgrade
 
exec airflow webserver  #start command for airflow webserver
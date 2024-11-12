#!/bin/bash
set -e   #script exit immediately if any command fails
 
if [ -e "/opt/airflow/requirements.txt" ]; then
  $(command python) pip install --upgrade pip
  $(command -v pip) install --user -r requirements.txt
fi
 
if [ ! -f "/opt/airflow/airflow.db" ]; then
  airflow db init && \
  airflow users create \
    --username PeterBroussaud \
    --firstname Peter \
    --lastname Broussaud \
    --role Admin \
    --email peter.broussaud@supdevinci-edu.fr \
    --password motdepasse
fi
 
$(command -v airflow) db upgrade
 
exec airflow webserver  #start command for airflow webserver
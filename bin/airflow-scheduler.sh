#!/bin/sh

airflow db upgrade

airflow pools -s default_pool ${AIRFLOW_DEFAULT_POOL_SLOTS:-16} "Main tasks"
airflow pools -s sensors ${AIRFLOW_SENSORS_POOL_SLOTS:-16} "External task sensors"

airflow scheduler

#!/bin/sh

airflow upgradedb

airflow pool -s default_pool ${AIRFLOW_DEFAULT_POOL_SLOTS:-16} "Main tasks"
airflow pool -s sensors ${AIRFLOW_SENSORS_POOL_SLOTS:-16} "External task sensors"

airflow scheduler

#!/bin/bash

require_variable() {
    local var_name var_val
    var_name=$1
    eval var_val=\$${var_name}

    if [ -z "${var_val}" ]; then
        echo "${var_name} is unset"
        exit 1
    fi
}

export AIRFLOW_BUCKET_JSON=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][] | select(.binding_name=="airflow-default-s3")')
export AIRFLOW_DB_JSON=$(echo $VCAP_SERVICES | jq -r '.["postgres"][] | select(.binding_name=="airflow-default-db")')
export AIRFLOW_REDIS_JSON=$(echo $VCAP_SERVICES | jq -r '.["redis"][] | select(.binding_name=="airflow-default-redis")')

export PYTHONPATH=/app:${PYTHONPATH}
export AIRFLOW_HOME=/home/vcap/app

export DEBUG=False

export AIRFLOW__CORE__DAGS_FOLDER=/home/vcap/app/${DAGS_REPO_NAME}/dags
export AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
export AIRFLOW__CORE__LOAD_EXAMPLES=False

export S3_IMPORT_DATA_BUCKET=$(echo $AIRFLOW_BUCKET_JSON | jq -r '.credentials.bucket_name')
export AWS_ACCESS_KEY_ID=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.aws_access_key_id')
export AWS_SECRET_ACCESS_KEY=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.aws_secret_access_key')
export AWS_DEFAULT_REGION=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.aws_region')
export AIRFLOW_CONN_DEFAULT_S3="s3://"$(echo $AIRFLOW_BUCKET_JSON | jq -r '.credentials | "\(.aws_access_key_id | @uri):\(.aws_secret_access_key | @uri)"')"@S3"

export AIRFLOW__CORE__SECURE_MODE=True
export AIRFLOW__CORE__DONOT_PICKLE=True
export AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True

export AIRFLOW__LOGGING__REMOTE_LOGGING=True
export AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=DEFAULT_S3
export AIRFLOW__LOGGING__ENCRYPT_S3_LOGS=True
export AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER="s3://"$(echo $AIRFLOW_BUCKET_JSON | jq -r '.credentials.bucket_name')"/logs"

export AIRFLOW__CORE__SQL_ALCHEMY_CONN=$(echo $AIRFLOW_DB_JSON | jq -r '.credentials.uri' | sed s/postgres:/postgresql:/)

export AIRFLOW__CORE__EXECUTOR=CeleryExecutor
export AIRFLOW__CELERY__BROKER_URL=$(echo $AIRFLOW_REDIS_JSON | jq -r '.credentials.uri')
export AIRFLOW__CELERY__RESULT_BACKEND="db+${AIRFLOW__CORE__SQL_ALCHEMY_CONN}"

export AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=300
export AIRFLOW__SCHEDULER__PRINT_STATS_INTERVAL=86400

export AIRFLOW__WEBSERVER__AUTHENTICATE=True
export AIRFLOW__WEBSERVER__COOKIE_SECURE=True
export AIRFLOW__WEBSERVER__COOKIE_SAMESITE=Lax
export AIRFLOW__API__ENABLE_EXPERIMENTAL_API=True
export AIRFLOW__API__AUTH_BACKEND=auth.api_auth_backend

require_variable AIRFLOW__CORE__FERNET_KEY
require_variable AIRFLOW__WEBSERVER__SECRET_KEY

# The symbolic links to pg_restore and psql are not correctly setup for some reason
rm /home/vcap/deps/0/bin/pg_dump
ln -s /home/vcap/deps/0/apt/usr/lib/postgresql/12/bin/pg_dump /home/vcap/deps/0/bin/pg_dump

rm /home/vcap/deps/0/bin/psql
ln -s /home/vcap/deps/0/apt/usr/lib/postgresql/12/bin/psql /home/vcap/deps/0/bin/psql

exec $@

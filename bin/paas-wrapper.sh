#!/bin/sh

require_variable() {
    local var_name var_val
    var_name=$1
    eval var_val=\$${var_name}

    if [ -z "${var_val}" ]; then
        echo "${var_name} is unset"
        exit 1
    fi
}

export PYTHONPATH=/app:${PYTHONPATH}
export AIRFLOW_HOME=/home/vcap/app/airflow
export DEBUG=False

export AIRFLOW__CORE__DAGS_FOLDER=/home/vcap/app/${DAGS_REPO_NAME}/dags
export AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
export AIRFLOW__CORE__LOAD_EXAMPLES=False

export S3_IMPORT_DATA_BUCKET=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.bucket_name')
export AIRFLOW_CONN_DEFAULT_S3="s3://"$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials | "\(.aws_access_key_id | @uri):\(.aws_secret_access_key | @uri)"')"@S3"

export AIRFLOW__CORE__SECURE_MODE=True
export AIRFLOW__CORE__DONOT_PICKLE=True
export AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True

export AIRFLOW__CORE__REMOTE_LOGGING=True
export AIRFLOW__CORE__REMOTE_LOG_CONN_ID=DEFAULT_S3
export AIRFLOW__CORE__ENCRYPT_S3_LOGS=True
export AIRFLOW__CORE__REMOTE_BASE_LOG_FOLDER="s3://"$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.bucket_name')"/logs"

export AIRFLOW__CORE__SQL_ALCHEMY_CONN=$(echo $VCAP_SERVICES | jq -r '.postgres[0].credentials.uri')

export AIRFLOW__CORE__EXECUTOR=CeleryExecutor
export AIRFLOW__CELERY__BROKER_URL=$(echo $VCAP_SERVICES | jq -r '.redis[0].credentials.uri')
export AIRFLOW__CELERY__RESULT_BACKEND="db+${AIRFLOW__CORE__SQL_ALCHEMY_CONN}"

export AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=86400
export AIRFLOW__SCHEDULER__PRINT_STATS_INTERVAL=86400

export AIRFLOW__WEBSERVER__AUTHENTICATE=True
export AIRFLOW__WEBSERVER__AUTH_BACKEND=auth.airflow_login
export AIRFLOW__WEBSERVER__COOKIE_SECURE=True
export AIRFLOW__WEBSERVER__COOKIE_SAMESITE=Lax

require_variable AIRFLOW__CORE__FERNET_KEY
require_variable AIRFLOW__WEBSERVER__SECRET_KEY

exec $@

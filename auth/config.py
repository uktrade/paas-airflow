"""A module that defines project wide config."""
import os

AUTHBROKER_CLIENT_ID = os.environ.get("AUTHBROKER_CLIENT_ID")
AUTHBROKER_CLIENT_SECRET = os.environ.get("AUTHBROKER_CLIENT_SECRET")
AUTHBROKER_ALLOWED_DOMAINS = os.environ.get("AUTHBROKER_ALLOWED_DOMAINS")
AUTHBROKER_URL = os.environ.get("AUTHBROKER_URL")

DEBUG = True if os.environ.get("DEBUG") == "True" else False
REDIS_URL = os.environ.get("AIRFLOW__CELERY__BROKER_URL")

S3_IMPORT_DATA_BUCKET = os.environ.get("S3_IMPORT_DATA_BUCKET")
S3_RETENTION_PERIOD_DAYS = os.environ.get("S3_RETENTION_PERIOD_DAYS", 7)

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

AIRFLOW_API_HAWK_CREDENTIALS = {
    os.environ.get("DATA_STORE_UPLOADER_SENDER_HAWK_ID"): os.environ.get("DATA_STORE_UPLOADER_SENDER_HAWK_KEY"),
}

DEFAULT_DATABASE_GRANTEES = (
    os.environ.get("DEFAULT_DATABASE_GRANTEES", "").split(",")
    if os.environ.get("DEFAULT_DATABASE_GRANTEES") is not None
    else []
)

web: /home/vcap/app/bin/checkout_dags.sh && /home/vcap/app/bin/paas-wrapper.sh airflow webserver -p 8080
worker: /home/vcap/app/bin/checkout_dags.sh && /home/vcap/app/bin/paas-wrapper.sh airflow celery worker
scheduler: /home/vcap/app/bin/checkout_dags.sh && /home/vcap/app/bin/paas-wrapper.sh /home/vcap/app/bin/airflow-scheduler.sh

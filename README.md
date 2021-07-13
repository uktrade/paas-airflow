# PaaS Airflow

PaaS Airflow is an example project for deploying Apache Airflow into Cloud Foundry PaaS.  This has the minimum airflow installation requirements for deploying onto GDS PaaS.  

For security, included in front of the airflow interface is staff sso.

deploying
---------

pre-reqs
  - please ensure the vars (see sample.env) are set before deploying
  - The following backing services are required, and must be bound with specific `binding-name`s, to avoid collisions with other services
      - postgres db: `cf bind-service app-instance-name pg-instance-name --binding-name airflow-default-db`
      - redis: `cf bind-service app-instance-name redis-instance-name --binding-name airflow-default-redis`
      - S3 bucket: `cf bind-service app-instance-name s3-instance-name --binding-name airflow-default-s3`
  - For the initial push you will need to initiate the DB, so the procfile should be updated to included (or v3-ssh into service and run the command)
      - /home/vcap/app/bin/paas-wrapper.sh airflow db init
      once done, remove this entry and put the procfile back to how it was.

This can be pushed to paas using the standard CF cli commands eg.

  - cf v3-push app-name

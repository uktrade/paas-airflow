# PaaS Airflow

PaaS Airflow is an example project for deploying Apache Airflow into Cloud Foundry PaaS.  This has the minimum airflow installation requirements for deploying onto GDS PaaS.  

For security, included in front of the airflow interface is staff sso.

deploying
---------

This can be pushed to paas using the standard CF cli commands eg.

cf push app-name

please ensure the vars (see sample.env) are set before deploying

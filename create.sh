#!/bin/bash
# work in progress, for now use the create_cluster.py script
cluster=$(databricks clusters create --json-file ./cluster.json | jq '.cluster_id')

databricks libraries install --cluster-id $cluster --jar dbfs:/home/dave.carlson@databricks.com/libs/automatedml_2.11-0.7.1.jar
databricks libraries install --cluster-id $cluster --whl dbfs:/home/dave.carlson@databricks.com/libs/pyAutoML-0.2.0-py3-none-any.whl

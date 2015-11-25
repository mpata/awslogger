# awslogger
A package to provide python logging handlers for multiple AWS services.

## Supported services
* CloudWatch Logs

## WIP
* DynamoDB
* SQS
* SNS

## Dependencies
* boto3
* botocore

## Usage
**CloudWatch Logs Handler**
```python
import awslogger
import boto3
import logging

handler = awslogger.CloudWatchLogsHandler(
				session=boto3.Session(), 
				log_group_name="myloggroup", 
				log_stream_prefix="demo-")
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Hello world!")
```

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
awslogger.CloudWatchLogsHandler(session=boto3.Session(), log_group_name="myloggroup", log_stream_prefix="demo-")
```

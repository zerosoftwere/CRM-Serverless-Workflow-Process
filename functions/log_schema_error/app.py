import time
import boto3
import json

client = boto3.client('logs')

def lambda_handler(event, context):
    payload = event['payload']
    logGroupName = event['logGroupName']
    logStreamName= event['logStreamName']
    try:
        message = json.dumps(payload)
    except:
        message = str(payload)

    client.put_log_events(
        logGroupName=logGroupName,
        logStreamName=logStreamName,
        logEvents=[
            {
                'timestamp': int(round(time.time() * 1000)),
                'message': message
            }
        ]
    )
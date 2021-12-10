import json
import boto3
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.info("event: {}".format(event))
    event_bus = os.environ['EVENT_BUS']#arn:aws:events:us-east-1:112520250899:event-bus/default
    message = event['Records'][0]['Sns']['Message']
    
    logger.info("From SNS: " + message)
    client = boto3.client("events")
    detail_message = message.replace("\n","#")
    logger.debug(detail_message)
    detail = {}
    detail["message"] = detail_message
    response = client.put_events(
    Entries=[
        {
            'Time': datetime.now(),
            'Source': 'budget-control-solution',
            'DetailType': 'Budget Threshold Breached',
            'Detail': json.dumps(detail),
            'EventBusName' : event_bus
        },
    ]
    )
    logger.debug(response)
    return response
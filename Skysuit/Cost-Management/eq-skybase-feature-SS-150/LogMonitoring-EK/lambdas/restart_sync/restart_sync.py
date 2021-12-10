# This lambda is designed to be manually invoked
# This script is meant to be used to "unpause" the message processing for allowing s3 sync of cloud trail log files to ElasticSearch.
# Invoking this script with any event will move all the messages from SQS queue specified in env variabe "DEAD_LETTER_QUEUE_URL"
# to SQS specified in env variable "MAIN_QUEUE_URL"
# Once the messages are moved the event source mapping identified by ebv variable "EVENTSOURCE_MAPPING_UUID" will be enabled

import json
import boto3
import os
import logging
from botocore.exceptions import ClientError


class EnvVariables:
    def __init__(self):          
        self.EVENTSOURCE_MAPPING_UUID = os.environ["EVENTSOURCE_MAPPING_UUID"]
        self.DEAD_LETTER_QUEUE_URL = os.environ["DEAD_LETTER_QUEUE_URL"]
        self.MAIN_QUEUE_URL = os.environ["MAIN_QUEUE_URL"]
        self.NOTIFICATION_TOPIC_ARN = os.environ["NOTIFICATION_TOPIC_ARN"]


def handler(event, context):
    try:
        print("Event Details: ", json.dumps(event))
        ENV_VARS = EnvVariables()

        client_lambda = boto3.client("lambda")
        # check for null
        MsgCount = move_messages(ENV_VARS.DEAD_LETTER_QUEUE_URL, ENV_VARS.MAIN_QUEUE_URL)
        # enable event source mapping
        client_lambda.update_event_source_mapping(UUID = ENV_VARS.EVENTSOURCE_MAPPING_UUID, Enabled = True)
        send_unpause_notification(_notification_topic_arn = ENV_VARS.NOTIFICATION_TOPIC_ARN, _context = context)

        # return message confirming enabling of event source mapping
        return {
            'statusCode': 200,
            'body': json.dumps(f'{MsgCount} messages moved from {ENV_VARS.DEAD_LETTER_QUEUE_URL} to {ENV_VARS.MAIN_QUEUE_URL}; Message processing has been restarted.')
            }

    except Exception as e:
        logger.error("Error resrating sync: " + str(e))
        raise e



def move_messages(_fromurl : str, _tourl: str) -> int:
    """
        Moves messaged from the SQS queue _fromurl to the SQS queue _tourl
    """
    print (f"Moving messages from {_fromurl} to {_tourl}")
    sqs_client = boto3.client('sqs')
    MsgCount = 0

    while True:
        messages = sqs_client.receive_message(QueueUrl=_fromurl, MaxNumberOfMessages=10, WaitTimeSeconds=10)
        if 'Messages' in messages:
            for m in messages['Messages']:
                print (f"moving message {MsgCount + 1}: {m['MessageId']} to main queue")
                ret = sqs_client.send_message( QueueUrl=_tourl, MessageBody=m['Body'])
                print (f"Deleting message {MsgCount + 1}: {m['MessageId']} from dlq")
                sqs_client.delete_message(QueueUrl=_fromurl, ReceiptHandle=m['ReceiptHandle'])
                MsgCount += 1
        else:
            print('Queue is currently empty or messages are invisible')
            break

    print (f"{MsgCount} messages moved from {_fromurl} to {_tourl}")
    return MsgCount


def send_unpause_notification(_notification_topic_arn, _context):
    """
    Sends an SNS notification with relevant information
    with reference to the specific Lambda function and the event source

    Arguments:
        _notification_topic_arn --> sns topic to use
        _context --> lambda context
    """

    # Grab region from topic arn
    OutboundTopicArn =   _notification_topic_arn
    SNSMessage =""
    Account = _context.invoked_function_arn.split(":")[4]

    sns_client = boto3.client('sns')
    # Build SNS Subject
    subject = f'Restarted - Sync has been restarted in Account: {Account}'
    SNSMessage = "Cloud trail log file syncronization has been restarted." + "\n"
    SNSMessage += "Messages have been moved from dead letter queue to main queue in order to be re processed" + "\n"

    # Publish to SNS Topic
    response = sns_client.publish(TopicArn=OutboundTopicArn,
                                Message=SNSMessage,
                                Subject=subject)
    print('--- Restart message sent: ---')


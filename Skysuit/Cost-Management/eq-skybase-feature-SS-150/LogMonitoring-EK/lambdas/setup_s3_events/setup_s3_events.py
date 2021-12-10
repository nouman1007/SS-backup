import json
import boto3
import logging
import os
import crhelper
from collections import namedtuple

s3 = boto3.client('s3')

# Initialize Logger
logger = crhelper.log_config({"RequestId": "CONTAINER_INIT"})
logger.info('Logging configured')

# set global to track init failures
init_failed = False

physical_resource_id = 's3-to-es-logs-replication'   # Compare with before

BucketInfo =   namedtuple('BucketInfo', 'AddThese RemoveThese')

class ResourceProperties:
      def __init__(self, _resourceproperties):
        SourceBucketsArns = _resourceproperties["SourceS3BucketsArnList"]
        self.bucket_arns = SourceBucketsArns.split(",")
        self.buckets = list(map(lambda x: x.split(":")[-1] , self.bucket_arns))
        print(self.buckets)
        self.sqs_queue_arn = _resourceproperties['SqsQueueArn']
        self.sqs_queue_url = _resourceproperties['SqsQueueUrl']


def create_sqs_policy(_sqs_queue_arn, _bucket_arns, _sqs_queue_url):

    # set up SNS policy to allow source buckets to write to topic
    sqs_queue_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "s3.amazonaws.com"
                },
                "Action": "sqs:SendMessage",
                "Resource": _sqs_queue_arn,
                "Condition": {
                    "ArnLike": {
                        "AWS:SourceArn": _bucket_arns
                    },
                },
            },
        ],
    }

    sqs_client = boto3.client('sqs')

    response = sqs_client.set_queue_attributes(
        QueueUrl= _sqs_queue_url,
        Attributes={
            'Policy': json.dumps(sqs_queue_policy)
        }
    )

    print('SQS Policy Response: ', response)


def create(event, context):
    response_data = {}
    NewResourceProperties = ResourceProperties(event.get("ResourceProperties"))
    enroll_buckets(NewResourceProperties, NewResourceProperties.buckets)

    return physical_resource_id, response_data
    

def enroll_buckets( newresources_: ResourceProperties, bucketstoenroll_):     
    
    create_sqs_policy(newresources_.sqs_queue_arn, newresources_.bucket_arns, newresources_.sqs_queue_url)   # update sqs polict to allow all 


    # Create notification events on each of the source buckets
    for bucket in bucketstoenroll_:
        print(f'Adding event to bucket: {bucket} for queue: {newresources_.sqs_queue_arn}')
        s3 = boto3.client('s3')
        response = s3.put_bucket_notification_configuration(
            Bucket=bucket,
            NotificationConfiguration={
                'QueueConfigurations': [
                    {
                        'Id': 'S3_Put_Events_To_SQS',
                        'QueueArn': newresources_.sqs_queue_arn,
                        'Events': [
                            's3:ObjectCreated:*',
                        ],
                    },
                ],
            }
        )
        print('Create S3 Event Response: ', response)

    

def update(event, context):
    response_data = {}
    
    OldResourceProperties = ResourceProperties(event["OldResourceProperties"])
    NewResourceProperties = ResourceProperties(event.get("ResourceProperties"))
    BucketInfo  = get_diff(OldResourceProperties.buckets, NewResourceProperties.buckets)
    delete_notification_configurations(BucketInfo.RemoveThese)
    enroll_buckets(NewResourceProperties, BucketInfo.AddThese)   # enroll only the newly added buckets. this is done to prevent momemtary blip where already enrolled buckets do not stop sending events
    
    return physical_resource_id, response_data

def delete(event, context):
    response_data = {}
    DeleteResourceProperties = ResourceProperties(event.get("ResourceProperties"))
    delete_notification_configurations(DeleteResourceProperties.buckets)
    
    return physical_resource_id, response_data

def delete_notification_configurations(_buckets):
    for bucket in _buckets:
        print(f'Deleting event from bucket: {bucket}')
        s3 = boto3.client('s3')
        response = s3.put_bucket_notification_configuration(
            Bucket=bucket,
            NotificationConfiguration={}
        )
        
        print('Reset S3 Event Response: ', response)

def handler(event, context):
    """
    Main handler function, passes off it's work to crhelper's cfn_handler
    """
    print('CloudFormation event received: %s' % json.dumps(str(event)))
    logger = crhelper.log_config(event)
    print("logging initiated")
    
    return crhelper.cfn_handler(event, context, create, update, delete, logger, init_failed)


def get_diff(listold_: list , listnew_: list) -> BucketInfo:
    createthese = []
    deletethese = []

    for elem in listnew_:
        if elem not in listold_: createthese.append(elem)

    for elem in listold_:
        if elem not in listnew_: deletethese.append(elem)

    return BucketInfo(createthese, deletethese)

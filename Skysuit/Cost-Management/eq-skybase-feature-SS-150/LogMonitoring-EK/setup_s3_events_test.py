import json
import logging
import threading
import os
import setup_s3_events




createevent = {
  "RequestType": "Create",
  "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
  "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A892576922991%3Astack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a%7CrSetupEventsLambdaInvoke%7C0d65d741-6012-4230-984e-f966a28d15db?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200128T180022Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWT6CCBT2N5%2F20200128%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=7dab5d1c8c9599647c0cf538dd09f32512ecee15de492f05478b3d14a069a765",
  "StackId": "arn:aws:cloudformation:us-east-1:892576922991:stack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a",
  "RequestId": "0d65d741-6012-4230-984e-f966a28d15db",
  "LogicalResourceId": "rSetupEventsLambdaInvoke",
  "ResourceType": "AWS::CloudFormation::CustomResource",
  "ResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail,arn:aws:s3:::834800198471-ab-cloudtrail,arn:aws:s3:::834800198471-cd-cloudtrail,arn:aws:s3:::834800198471-ef-cloudtrail"
  }
}

Updateevent = {
  "RequestType": "Update",
  "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
  "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A892576922991%3Astack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a%7CrSetupEventsLambdaInvoke%7C0d65d741-6012-4230-984e-f966a28d15db?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200128T180022Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWT6CCBT2N5%2F20200128%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=7dab5d1c8c9599647c0cf538dd09f32512ecee15de492f05478b3d14a069a765",
  "StackId": "arn:aws:cloudformation:us-east-1:892576922991:stack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a",
  "RequestId": "0d65d741-6012-4230-984e-f966a28d15db",
  "LogicalResourceId": "rSetupEventsLambdaInvoke",
  "ResourceType": "AWS::CloudFormation::CustomResource",
  "ResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail,arn:aws:s3:::834800198471-ab-cloudtrail,arn:aws:s3:::834800198471-cd-cloudtrail,arn:aws:s3:::834800198471-gh-cloudtrail"
  },
  "OldResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail,arn:aws:s3:::834800198471-ab-cloudtrail,arn:aws:s3:::834800198471-cd-cloudtrail,arn:aws:s3:::834800198471-ef-cloudtrail"
  }
}

Updateevent_remove_buckets = {
  "RequestType": "Update",
  "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
  "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A892576922991%3Astack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a%7CrSetupEventsLambdaInvoke%7C0d65d741-6012-4230-984e-f966a28d15db?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200128T180022Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWT6CCBT2N5%2F20200128%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=7dab5d1c8c9599647c0cf538dd09f32512ecee15de492f05478b3d14a069a765",
  "StackId": "arn:aws:cloudformation:us-east-1:892576922991:stack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a",
  "RequestId": "0d65d741-6012-4230-984e-f966a28d15db",
  "LogicalResourceId": "rSetupEventsLambdaInvoke",
  "ResourceType": "AWS::CloudFormation::CustomResource",
  "ResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail,arn:aws:s3:::834800198471-ab-cloudtrail,arn:aws:s3:::834800198471-ef-cloudtrail"
  },
  "OldResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail,arn:aws:s3:::834800198471-ab-cloudtrail,arn:aws:s3:::834800198471-cd-cloudtrail,arn:aws:s3:::834800198471-ef-cloudtrail"
  }
}


Updateevent_add_buckets = {
  "RequestType": "Update",
  "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
  "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A892576922991%3Astack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a%7CrSetupEventsLambdaInvoke%7C0d65d741-6012-4230-984e-f966a28d15db?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200128T180022Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWT6CCBT2N5%2F20200128%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=7dab5d1c8c9599647c0cf538dd09f32512ecee15de492f05478b3d14a069a765",
  "StackId": "arn:aws:cloudformation:us-east-1:892576922991:stack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a",
  "RequestId": "0d65d741-6012-4230-984e-f966a28d15db",
  "LogicalResourceId": "rSetupEventsLambdaInvoke",
  "ResourceType": "AWS::CloudFormation::CustomResource",
  "ResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail,arn:aws:s3:::834800198471-ab-cloudtrail,arn:aws:s3:::834800198471-cd-cloudtrail,arn:aws:s3:::834800198471-ef-cloudtrail,arn:aws:s3:::834800198471-gh-cloudtrail"
  },
  "OldResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail,arn:aws:s3:::834800198471-ab-cloudtrail,arn:aws:s3:::834800198471-cd-cloudtrail,arn:aws:s3:::834800198471-ef-cloudtrail"
  }
}

deleteevent = {
  "RequestType": "Delete",
  "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
  "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A892576922991%3Astack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a%7CrSetupEventsLambdaInvoke%7C0d65d741-6012-4230-984e-f966a28d15db?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200128T180022Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWT6CCBT2N5%2F20200128%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=7dab5d1c8c9599647c0cf538dd09f32512ecee15de492f05478b3d14a069a765",
  "StackId": "arn:aws:cloudformation:us-east-1:892576922991:stack/s3RelpicationV2/325e0150-41e1-11ea-b74d-0aa958b6917a",
  "RequestId": "0d65d741-6012-4230-984e-f966a28d15db",
  "LogicalResourceId": "rSetupEventsLambdaInvoke",
  "ResourceType": "AWS::CloudFormation::CustomResource",
  "ResourceProperties": {
    "ServiceToken": "arn:aws:lambda:us-east-1:892576922991:function:s3RelpicationV2-rSetupS3BucketEventsLambda-1JQTRE6R5BAMF",
    "SqsQueueArn" :"arn:aws:sqs:us-east-1:834800198471:ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SqsQueueUrl" : "https://sqs.us-east-1.amazonaws.com/834800198471/ST-s3Sync11-rMainSqsQueue-196HFGCK4KX96",
    "SourceS3BucketsArnList" : "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail"
  }
}

class context:
    aws_request_id = 'aaa89780780b8yu080j0mjh0'
    invoked_function_arn = "arn:aws:lambda:us-east-1:834800198471:function:St-GuardDuty"
    log_stream_name = "log stream"
    def get_remaining_time_in_millis(self) -> float:
        return 6000000.00
context = context()


# os.environ["SourceS3BucketsArnList"] = "arn:aws:s3:::834800198471-eb-cloudtrail,arn:aws:s3:::834800198471-sb-cloudtrail"

# os.environ['SqsQueueArn'] = "arn:aws:sqs:us-east-1:834800198471:St-s3syncv6-rMainSqsQueue-1M5UD6KUP9E7A"
# os.environ['SqsQueueUrl'] = "https://sqs.us-east-1.amazonaws.com/834800198471/St-s3syncv6-rMainSqsQueue-1M5UD6KUP9E7A"
 
# import crhelper
import setup_s3_events

print("CREATE ################################################")
setup_s3_events.handler(createevent,context)
print("UPDATE ################################################")

# setup_s3_events.handler(Updateevent,context)   # remove ef add gh
# setup_s3_events.handler(Updateevent_add_buckets,context)   # add gh nothing to remove
# setup_s3_events.handler(Updateevent_remove_buckets,context)   # remove cd nothing to add




# aaa = setup_s3_events.s3






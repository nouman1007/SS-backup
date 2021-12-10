import traceback
import logging
import boto3
import json
import os
import urllib3

from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global environment variables 
SUCCESS = "SUCCESS"
FAILED = "FAILED"


http = urllib3.PoolManager() 

def lambda_handler(event, context):

    logger.info('In Main Lambda Handler.')
    logger.info(json.dumps(event))

    provider_arn = None
    responseData = {}

    try:

        if event['RequestType'] == 'Create':
            provider_arn = create_policy(event)
        elif event['RequestType'] == 'Update':
            provider_arn = event['PhysicalResourceId']
            update_policy(event)
        elif event['RequestType'] == 'Delete':
            provider_arn = event['PhysicalResourceId']
            delete_policy(event)
        else:
            raise Exception("Unknown operation: " + event['RequestType'])
        
        send(event, context, SUCCESS, responseData, provider_arn)
    
    except Exception as e:
        logger.error(e)
        send(event, context, FAILED, responseData, provider_arn, str(e))

def getpolicymetadata(event):
    return event['ResourceProperties']['PolicyName'], event['ResourceProperties']['PolicyDoc'], event['ResourceProperties']['PolicyType'], event['ResourceProperties']['Description']

def create_policy(event):

    logger.info("in create")
    policyname, policyjson, policytype, policydescription = getpolicymetadata(event)

    client = boto3.client('organizations')
    resp = client.create_policy(
        Content=json.dumps(policyjson),
        Description=policydescription,
        Name=policyname,
        Type=policytype)

    return resp['Policy']['PolicySummary']['Arn']


def update_policy(event):

    logger.info("in Update")
    policyname, policyjson, policytype, policydescription = getpolicymetadata(event)

    PolicyId = event['PhysicalResourceId'].split('/')[-1]

    client = boto3.client('organizations')
    resp = client.update_policy(
        PolicyId=PolicyId,
        Content=json.dumps(policyjson),
        Description=policydescription,
        Name=policyname,
        )

    return

def delete_policy(event):

    logger.info("in delete")
    PolicyId = event['PhysicalResourceId'].split('/')[-1]

    client = boto3.client('organizations')
    resp = client.delete_policy(
        PolicyId=PolicyId
        )
    return



def send(event, context, responseStatus, lambda_info, physicalResourceId=None, reason=None,
         noEcho=False):
    """Send CFN Response."""
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = ('' if reason is None else f"{reason} " ) + 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = lambda_info

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }
    try:
        response = http.request('PUT',responseUrl,headers=headers,body=json_responseBody)
        logger.info("Status code: {}".format(str(response.status)))
    except Exception as e:
        logger.error("send(..) failed executing requests.put(..): " + str(e))

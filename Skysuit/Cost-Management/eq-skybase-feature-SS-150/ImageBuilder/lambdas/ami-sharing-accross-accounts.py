import json
import boto3
import logging
import time
import datetime
import os
          
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sts_connection = boto3.client('sts')
acct_b = sts_connection.assume_role(
    RoleArn= os.environ['AssumeRoleArn'],
    RoleSessionName="cross_acct_lambda"
    )
    
ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
SESSION_TOKEN = acct_b['Credentials']['SessionToken']
         
ec2 = boto3.client('ec2')
organization_client = boto3.client('organizations', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN,)

class Const():
    KEY_NEXT_TOKEN      = "NextToken"
    KEY_ACCOUNTS        = 'Accounts'
    

def lambda_handler(event, context):
    
    logger.info('Event:' + str(event))

    organization_accounts = []
    
    FILTER_CRITERIA = json.loads( os.environ.get('FILTER', '[{"Name": "tag:share","Values": ["true"]}]'))
            

    try:
        response = organization_client.list_accounts()
        organization_accounts += response[Const.KEY_ACCOUNTS]
   
        while(Const.KEY_NEXT_TOKEN in response.keys()):
            response = organization_client.list_accounts(NextToken = response[Const.KEY_NEXT_TOKEN])
            organization_accounts += response[Const.KEY_ACCOUNTS]
            
    except Exception as e:
        logger.error("send(..) failed to get account information: " + str(e)) 
   
    organization_accounts = [org_account['Id'] for org_account in organization_accounts]
    
    amis= ec2.describe_images(Owners=['self'],Filters=FILTER_CRITERIA)['Images']
            
    for ami in amis:
        image_id = ami['ImageId']
        print(image_id)
            
        ec2.modify_image_attribute(
            ImageId = ami['ImageId'],
            OperationType='add',
            Attribute='launchPermission',
            UserIds=organization_accounts
        )
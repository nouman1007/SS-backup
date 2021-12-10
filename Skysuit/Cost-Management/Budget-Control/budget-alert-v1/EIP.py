import boto3
from botocore.exceptions import ClientError
import time
import datetime
import os
import json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

client = boto3.client('ses')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
NOTIFICATION_EMAIL_MAPPING = os.environ['NOTIFICATION_EMAIL_MAPPING']

# {
  # "773732177525": {
    # "email": "SRathinavelu@enquizit.com"
  # },
  # "269020512649": {
    # "email": "jaslam@enquizit.com"
  # },
  # "089208736206": {
    # "email": "arun@enquizit.com"
  # },
  # "834800198471": {
    # "email": "sthanushkodi@enquizit.com"
  # },
  # "566241887797": {
    # "email": "abhanji@enquizit.com"
  # },
  # "429247474025": {
    # "email": "hmengistu@enquizit.com"
  # },
  # "076028080430": {
    # "email": "njaved@enquizit.com"
  # },
  # "673633873796": {
    # "email": "ddoten@enquizit.com"
  # },
  # "163112212549": {
    # "email": "gkhan@enquizit.com"
  # },
  # "924871970822": {
    # "email": "hiqbal@enquizit.com"
  # },
  # "960302243882": {
    # "email": "ikothandaraman@enquizit.com"
  # },
  # "173803080401": {
    # "email": "jaslam@enquizit.com"
  # },
  # "935552933057": {
    # "email": "mahmad@enquizit.com"
  # },
  # "221870271996": {
    # "email": "nsardar@enquizit.com"
  # },
  # "742111853221": {
    # "email": "nshafiq@enquizit.com"
  # },
  # "971642970976": {
    # "email": "njaved@enquizit.com"
  # },
  # "434986650141": {
    # "email": "prasanna@enquizit.com"
  # },
  # "498573059777": {
    # "email": "mjunaid@enquizit.com"
  # },
  # "459273849936": {
    # "email": "sdutta@enquizit.com"
  # },
  # "110330507156": {
    # "email": "shu@enquizit.com"
  # },
  # "682213185593": {
    # "email": "uakram@enquizit.com"
  # },
  # "017270171827": {
    # "email": "kramakur@enquizit.com"
  # },
  # "018599439328": {
    # "email": "sgopinath@enquizit.com"
  # },
  # "936938745355": {
    # "email": "szamfir@enquizit.com"
  # }
# }

def lambda_handler(event, context):
  # Get list of account in the organisation using the function defined below
    Accounts=get_active_account_list()
  # Looping all over the available accounts
    for AccountID in Accounts:
        list_IP=""
        counter1=1
        Unused_EIP="false"       
        try:
            AccountID =str(AccountID["Id"])
            # logger.info('Event: ' + str(event))
            print ("======================================")
            print("Account ID is ",AccountID)
            print ("======================================")
            logger.info(f"source account ID: {​AccountID}​")
            ROLE_NAME = "OrganizationAccountAccessRole"
            sts_connection = boto3.client('sts')
            RoleArn= f"arn:aws:iam::{​AccountID}​:role/{​ROLE_NAME}​"
            acct_ = sts_connection.assume_role(RoleArn= RoleArn,RoleSessionName= f"EventSession{​AccountID}​")
            credentials=acct_['Credentials']
            # Key ID and Access keys of the account where the EIP  is created
            clientEC2 = boto3.client(
              'ec2',
              aws_access_key_id= credentials['AccessKeyId'],
             aws_secret_access_key= credentials['SecretAccessKey'],
              aws_session_token= credentials['SessionToken'],
              )
            # Obtaining list of EIPs
            addresses_dict = clientEC2.describe_addresses()
            print("Existing EIPs in this account are listed below")
            for eip_list in addresses_dict['Addresses']:
                if "NetworkInterfaceId" not in eip_list:
                    Unused_EIP="true"
                    print(eip_list['PublicIp'])
                    Elastic_IP=eip_list['PublicIp']
                    list_IP=list_IP+str(counter1)+") "+str(Elastic_IP)+"\n"
                    counter1= counter1+1
                    Tag = clientEC2.create_tags(
                        Resources=[
                            eip_list['AllocationId'],
                            ],
                            Tags=[
                                {​
                                    'Key': 'Scheduled for Release',
                                    'Value': '3days'
                                }​
                            ]
                        )
                    send_email("sdutta@enquizit.com",str(str(get_notificationemail_for_account(AccountID))),str(list_IP), "us-east-1", AccountID)                        
        except Exception as e:
            logger.error('Something went wrong: ' + str(e))
            raise e     

			
def get_active_account_list(): 
            #     """
            #   This function returns list of active accounts
            # """
            client = boto3.client('organizations')
            resAccounts = client.list_accounts_for_parent(ParentId= 'ou-xsd9-97ogq174') 
            Accounts = resAccounts["Accounts"]  #['Accounts'[{​'Status':'ACTIVE'}​]]   
            return Accounts
			
			
def get_notificationemail_for_account(accountid):
    #     ACOUNT_NOTIFICATION_CONFIG_JASON = json.loads(ACOUNT_NOTIFICATION_CONFIG)
    #     ret = jmespath.search(f"Accounts[?id== '{​accountid_}​'].owneremail", ACOUNT_NOTIFICATION_CONFIG_JASON)
    #     return ret
    Notification_email = json.loads(NOTIFICATION_EMAIL_MAPPING)
    if (accountid in Notification_email) and ("email" in Notification_email[accountid]) :
        owneremail = str(Notification_email[accountid]["email"])                # "szamfir@enquizit.com"
    else:
        raise Exception(f"email not configured in NOTIFICATION_EMAIL_MAPPING for account {​accountid}​")
    return owneremail
	
	
	
# This function send an SES email
def send_email(sender,recipient, list, aws_region, accountID):
       # This address must be verified with Amazon SES.
       SENDER = sender
       # If your account is still in the sandbox, this address must be verified.
       RECIPIENT =recipient
       list3=list
       # The AWS Region you're using for Amazon SES.
       AWS_REGION = aws_region
       # The subject line for the email.
       SUBJECT ="Releasing_Elastic_IP, in AWS account with ID:"+str(accountID)
       # The email body for recipients with non-HTML email clients.
       BODY_TEXT = " Dear IAM user,\n The  Elastic IP you created in AWS account with ID: " +str(accountID)+  " has been in Unallocated state. This email is to notify you the release of the IP. If you want to reserver an IP in the future, please tag the EIPs with a key reserveIP  with key value yes so that it will not be released autoamtically."  " \n The list for the EIPS are given below. \n " + list3 +  ". \n  \n Regards,  \nThe internal IT service Desk team"
       # The HTML body of the email.
       BODY_HTML = """<html> <head></head> <body> <h1>Release of unused or unatached Elastic IP</h1> <p> Dear IAM user,<p>  <br> The  Elastic IP  you created has been in Unallocated state. This email is to notify the release of the IP. If you want to reserver an Elastic IP in the future, please tag the elastic IP with a key "reserveIP"  with key value "yes" so that it will not be released autoamtically <br> Regards,</p>  <br> The internal IT service Desk team"""            
       # The character encoding for the email.
       CHARSET = "UTF-8"
       # Create a new SES resource and specify a region.
       clientSES = boto3.client('ses',region_name= AWS_REGION)
       # Try to send the email.
       try:
           #Provide the contents of the email.
           response = clientSES.send_email(
               Destination={​
                   'ToAddresses': [
                       RECIPIENT,
                   ],
               }​,
               Message={​
                   'Body': {​
                    #   'Html': {​
                    #       'Charset': CHARSET,
                    #       'Data': BODY_HTML,
                    #   }​,
                       'Text': {​
                           'Charset': CHARSET,
                           'Data': BODY_TEXT,
                       }​,
                   }​,
                   'Subject': {​
                       'Charset': CHARSET,
                       'Data': SUBJECT,
                   }​,
               }​,
               Source=SENDER,
         )
       # Display an error if something goes wrong. 
       except ClientError as e:
           return(e.response['Error']['Message'])
       else:
           return("Email sent! Message ID:" + response['MessageId'] )
    
    
  
  

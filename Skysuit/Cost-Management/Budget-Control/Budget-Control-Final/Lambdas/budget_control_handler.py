import boto3
import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#process the Budget event, move the user into QUARANTINE OU & send him notification email 
def process_budget_event(account_id, budget_config, dest_org_id):
  config_map = budget_config.split("#")
  if config_map:
    alert_type_config = config_map[3]
    budgeted_amount_config = config_map[2]
    acctual_amount_config  = config_map[5]
    
    if alert_type_config:
      logger.debug("Alert Type Config:{}".format(alert_type_config))
      alert_type = alert_type_config.split(":")[1].strip()
      logger.debug("Alert Type:{}".format(alert_type))
      logger.info('===============budgeted_amount========================')
      budgeted_amount = float (budgeted_amount_config.split(":")[1].split("$")[1])
      logger.debug("budgeted_amount:{}".format(budgeted_amount))
      acctual_amount = float (acctual_amount_config.split(":")[1].split("$")[1])
      logger.debug("acctual_amount:{}".format(acctual_amount))
      logger.info('======================================================')
      acct_list,source_org_id = get_active_account_list(account_id)
      logger.debug("Source-Org:{}".format(source_org_id))
      logger.debug("Acct_List:{}".format(acct_list))
      
      
      emails=[]
      for acct in acct_list:
        print(acct)
        emails.append(acct['Email'])
      logger.debug("Email Addresses:{}".format(emails))
      logger.info(emails)
      recipient = ["nshafiq@enquizit.com"] #emails

      if alert_type and alert_type in ["FORECASTED", "ACTUAL"]:
        if acctual_amount >= ((budgeted_amount)*80/100) and acctual_amount <= budgeted_amount:
          alert_message = "Budget Threshold reached for account {} on 80%, the account will has been restricted to create new resources on 100% to prevent incurring additional charges".format(account_id)
          send_email("skybase-master@enquizit.com", recipient, 'us-east-1', account_id, alert_message)
          logger.debug("Budgeted Amount on 80%:{}".format((budgeted_amount)*80/100))
        elif acctual_amount >= budgeted_amount:
          message = "Budget Threshold reached for account {} on 100% of its limit, the account has been restricted to create new resources on 100% to prevent incurring additional charges, Please contact your administrator".format(account_id)
          send_email("skybase-master@enquizit.com", recipient, 'us-east-1', account_id, message)
          if dest_org_id:
            print(dest_org_id)
            logger.debug("Destination OU:{}".format(dest_org_id))
          if source_org_id != dest_org_id:
            Tag_Resource(account_id, 'Origin-OU-ID', source_org_id)
            Tag_Resource(account_id, 'KeepQuarantine', 'False')

            Move_Account(account_id, source_org_id, dest_org_id)
            logger.debug("Budgeted Amount on 100%:{}".format(budgeted_amount))
        else:
            print("Budgeted Amount not found")
            logger.info('Budgeted Amount not found')

#Get the users account id & emial addresses from organization unit
def get_active_account_list(account_id):
    
    #     """
    #   This function returns list of active accounts
    # """
    client = boto3.client('organizations')
    Dest_Org_Id = 'ou-hlvo-7vgmf82j'#os.environ["QUARANTINE_OU"]
    if account_id == Dest_Org_Id:
        resAccounts = client.list_accounts_for_parent(ParentId= account_id)  #Todo: implement next token mechanism  
        Accounts = resAccounts["Accounts"]
        while "NextToken" in resAccounts:
            resAccounts = client.list_accounts_for_parent(ParentId= account_id, NextToken=resAccounts["NextToken"])
            Accounts.extend(resAccounts["Accounts"])
        return Accounts
    else:
        source_org_id = client.list_parents(ChildId=account_id)["Parents"][0]["Id"]
        resAccounts = client.list_accounts_for_parent(ParentId= source_org_id)  #Todo: implement next token mechanism  
        Accounts = resAccounts["Accounts"]
        while "NextToken" in resAccounts:
            resAccounts = client.list_accounts_for_parent(ParentId= source_org_id, NextToken=resAccounts["NextToken"])
            Accounts.extend(resAccounts["Accounts"])
        return Accounts,source_org_id

# Move the user from one OU to another
def Move_Account(Account_id, Source_org_id, Dest_org_id): 

    org_client = boto3.client("organizations")
    
    try:
      response = org_client.move_account(
      AccountId=Account_id,
      SourceParentId=Source_org_id,
      DestinationParentId=Dest_org_id
      )
      # return response
    except NameError:
      return NameError
    else:
      return response

# send email to users through AWS(SES)
def send_email(Sender, Recipient, aws_region, accountID, Message):
  SENDER = Sender
  RECIPIENT = Recipient
  AWS_REGION = aws_region
  SUBJECT = "Budget_Threshold_Aleret, in AWS account with ID:"+str(accountID)
  # BODY_TEXT = " Dear IAM user,\n The  Elastic IP you created in AWS account with ID: " +str(accountID)+  " has been in Unallocated state. This email is to notify you the release of the IP. If you want to reserver an IP in the future, please tag the EIPs with a key reserveIP  with key value yes so that it will not be released autoamtically."  " \n The list for the EIPS are given below. \n " + list3 +  ". \n  \n Regards,  \nThe internal IT service Desk team"
  # BODY_TEXT = " Dear IAM user,\n The Budget Threshold reached for account :"+str(accountID)+" has reached 80%, when it will be reached 100% of budget threshold the account will be restricted to create new resources, in oder  to prevent incurring additional charges".
  BODY_TEXT = Message
  BODY_HTML = """<html> <head></head> <body> <h1> Budget Threshold alert </h1> <p> Dear IAM user,<p>  <br> The Budget Threshold reached for account :"+str(accountID)+" has reached 80%, when it will be reached 100% of budget threshold the account will be restricted to create new resources, in oder  to prevent incurring additional charges" <br> Regards,</p>  <br> The internal IT service Desk team"""            
  # BODY_HTML = """<html> <head></head> <body> <h1>Release of unused or unatached Elastic IP</h1> <p> Dear IAM user,<p>  <br> The  Elastic IP  you created has been in Unallocated state. This email is to notify the release of the IP. If you want to reserver an Elastic IP in the future, please tag the elastic IP with a key "reserveIP"  with key value "yes" so that it will not be released autoamtically <br> Regards,</p>  <br> The internal IT service Desk team"""
  CHARSET = "UTF-8"

  clientSES = boto3.client('ses',region_name= AWS_REGION)

  try:
    response = clientSES.send_email(
      Destination = {
        'ToAddresses':RECIPIENT #[
          # RECIPIENT,
        # ]
      },
      Message = {
        'Subject':{
          'Data': SUBJECT,
          'Charset': CHARSET
        },
        'Body':{
            'Text':{
              'Charset': CHARSET,
              'Data': BODY_TEXT
            }
          }
        },
      Source = SENDER,
    )
  except NameError:
    return NameError
  else:
    return("Email sent! Message ID:" + response['MessageId'] )

# Attach tags with the user or account before move into QUARANTINE OU
def Tag_Resource(Account_Id, key, Origin_OU):

    client = boto3.client('organizations')
    
    try:
      response = client.tag_resource(
          ResourceId=Account_Id,
          Tags=[
              {
                  'Key': key,
                  'Value': Origin_OU
              },
          ]
      )
    except NameError:
      return NameError
    else:
      return response

# List the tags from QUARANTINE OU
def List_tags(resource_id):

    client = boto3.client('organizations')
    try:
      response = client.list_tags_for_resource(
      ResourceId=resource_id,
      # NextToken='string'
      )
    except NameError:
      return NameError
    else:
      return response
    
# Untag the user or account before sending back to its origin OU   
def Un_tag(Account_Id,Key):

    client = boto3.client('organizations')
    try:

      response = client.untag_resource(
      ResourceId= Account_Id,
      TagKeys=Key
      )
    except NameError:
      return NameError
    else:
      return response


def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.debug("Received:{}".format(event))
    status_code = "200"
    logger.info('In Main Lambda Handler.')
    dest_org_id = 'ou-hlvo-7vgmf82j' #os.environ["QUARANTINE_OU"]

    
    if event["detail"]:
        logger.info('Moving User to QUARANTINE OU')

        try:
          # dest_org_id = 'ou-hlvo-7vgmf82j' #os.environ["QUARANTINE_OU"]
          account_id = event["account"]
          logger.debug("Account id:{}".format(account_id))
          details = event["detail"]["message"]
          budget_config = details.split("##")[3]  #Budget Name: cost-managment-test#Budget Type: Cost#Budgeted Amount: $0.50#Alert Type: ACTUAL#Alert Threshold: > $0.20#ACTUAL Amount: $0.45
          logger.debug("BudgetDetails:{}".format(budget_config))
          process_budget_event(account_id, budget_config, dest_org_id)

        except Exception as e:
            logger.error(e)
            status_code=500
    else:
        logger.info('Moving Users Back From QUARANTINE OU')
        
        try:
          acct_list = get_active_account_list(dest_org_id)
          Account_Ids=[]
          for acct in acct_list:
              Account_Ids.append(acct['Id'])
          logger.debug("Account Ids in QUARANTINE OU :{}".format(Account_Ids))

          for act in Account_Ids:
              Tag = List_tags(act)
              logger.debug("Tags :{}".format(Tag))
              tgs=Tag['Tags']
              Keys = []
              tags = {}
              for ts in tgs:
                  tags[ts['Key']] = ts['Value']
                  Keys.append(ts['Key'])
              logger.debug("Keys :{}".format(Keys))

              if tags.get('KeepQuarantine') == 'False':
                  Un_tag(act,Keys)
                  Move_Account(act, dest_org_id, tags.get('Origin-OU-ID'))
                  logger.debug("Origin-OU-ID :{}".format(tags.get('Origin-OU-ID')))
              else:
                  logger.info('KeepQuarantine tag value is True')
                  
        except Exception as e:
            logger.error(e)
            status_code=500

    return {
        'statusCode': status_code,
        'body': json.dumps('Processed the EventBridge event')
    }



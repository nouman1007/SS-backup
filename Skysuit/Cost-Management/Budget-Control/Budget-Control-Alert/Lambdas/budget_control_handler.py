import boto3
import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
      print("===============budgeted_amount========================")
      budgeted_amount = float (budgeted_amount_config.split(":")[1].split("$")[1])
      logger.debug("budgeted_amount:{}".format(budgeted_amount))
      acctual_amount = float (acctual_amount_config.split(":")[1].split("$")[1])
      logger.debug("acctual_amount:{}".format(acctual_amount))
      print("======================================================")
      acct_list,source_org_id = get_active_account_list(account_id)
      logger.debug("Source-Org:{}".format(source_org_id))
      logger.debug("Acct_List:{}".format(acct_list))
      emails=[]
      for acct in acct_list:
        print(acct)
        emails.append(acct['Email'])
      print(emails[0])
      recipient = "nshafiq@enquizit.com"

      if alert_type and alert_type in ["FORECASTED", "ACTUAL"]:
        if acctual_amount >= ((budgeted_amount)*80/100) and acctual_amount <= budgeted_amount:
          alert_message = "Budget Threshold reached for account {} on 80%, the account will has been restricted to create new resources on 100% to prevent incurring additional charges".format(account_id)
          send_email("skybase-master@enquizit.com", recipient, 'us-east-1', account_id, alert_message)

          print("yes 80%")
        elif acctual_amount >= budgeted_amount:
          message = "Budget Threshold reached for account {} on 100% of its limit, the account has been restricted to create new resources on 100% to prevent incurring additional charges, Please contact your administrator".format(account_id)
          send_email("skybase-master@enquizit.com", recipient, 'us-east-1', account_id, message)
          if dest_org_id:
            print(dest_org_id)
          if source_org_id != dest_org_id:
            Move_Account(account_id, source_org_id, dest_org_id)
          print("yes 100%")
        else:
          print("try again")
        print("=====================================================")




def get_active_account_list(account_id):   # todo: implement nextoken
    #     """
    #   This function returns list of active accounts
    # """
    client = boto3.client('organizations')
    # resAccounts = client.list_accounts_for_parent(ParentId= ouid)  #Todo: implement next token mechanism  
    source_org_id = client.list_parents(ChildId=account_id)["Parents"][0]["Id"]
    resAccounts = client.list_accounts_for_parent(ParentId= source_org_id)  #Todo: implement next token mechanism  
    Accounts = resAccounts["Accounts"]
    while "NextToken" in resAccounts:
        resAccounts = client.list_accounts_for_parent(ParentId= source_org_id, NextToken=resAccounts["NextToken"])
        Accounts.extend(resAccounts["Accounts"])


    # source_org_id = g_id.list_parents(ChildId=account_id)["Parents"][0]["Id"]

        # temporary
    # Accounts = [{
    #         "Id": "834800198471",
    #         "Arn": "string",
    #         "Email": "hiruytyy@yahoo.com",
    #         "Name": "string",
    #         "Status": "ACTIVE",
    #         "JoinedMethod": "INVITED"
    # },
    # {
    #         "Id": "947827719635",
    #         "Arn": "string",
    #         "Email": "hiruytyy@yahoo.com",
    #         "Name": "string",
    #         "Status": "ACTIVE",
    #         "JoinedMethod": "INVITED"
    # },
    # {
    #         "Id": "459273849936",
    #         "Arn": "string",
    #         "Email": "hiruytyy@yahoo.com",
    #         "Name": "string",
    #         "Status": "ACTIVE",
    #         "JoinedMethod": "INVITED"
    # }
    #         ]
    return Accounts,source_org_id



def Move_Account(Account_id, Source_org_id, Dest_org_id):

    org_client = boto3.client("organizations")

    response = org_client.move_account(
    AccountId=Account_id,
    SourceParentId=Source_org_id,
    DestinationParentId=Dest_org_id
    )
    return response


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
        'ToAddresses': [
          RECIPIENT,
        ]
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


def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.debug("Received:{}".format(event))
    status_code = "200"
    try:
      dest_org_id = 'ou-hlvo-7vgmf82j' #os.environ["QUARANTINE_OU"]
      account_id = event["account"]
      
      logger.debug("Account id:{}".format(account_id))
      details = event["detail"]["message"]
      budget_config = details.split("##")[3]  #Budget Name: cost-managment-test#Budget Type: Cost#Budgeted Amount: $0.50#Alert Type: ACTUAL#Alert Threshold: > $0.20#ACTUAL Amount: $0.45
      logger.debug("BudgetDetails:{}".format(budget_config))
      process_budget_event(account_id, budget_config, dest_org_id)

    except Exception as e:
        logger.error(e)
        status_code=500
    return {
        'statusCode': status_code,
        'body': json.dumps('Processed the EventBridge event')
    }


# if __name__ == '__main__':
#     event = {
#   'version': '0',
#   'id': '12d5ea42-f376-fd64-4de4-674d5ffbf38c',
#   'detail-type': 'Budget Threshold Breached',
#   'source': 'budget-control-solution',
#   'account': '522955560990',
#   'time': '2021-06-27T01:14:54Z',
#   'region': 'us-east-1',
#   'resources': [
    
#   ],
#   'detail': {
#     'message': 'AWS Budget Notification June 27, 2021#AWS Account 522955560990##Dear AWS Customer,##You requested that we alert you when the ACTUAL Cost associated with your cost-managment-test budget is greater than $0.20 per day. Yesterday, the ACTUAL Cost associated with this budget is $0.45. You can find additional details below and by accessing the AWS Budgets dashboard [1].##Budget Name: cost-managment-test#Budget Type: Cost#Budgeted Amount: $100#Alert Type: ACTUAL#Alert Threshold: > $80#ACTUAL Amount: $81##[1] https://console.aws.amazon.com/billing/home#/budgets#'
#   }
# }
#     lambda_handler(event, None)
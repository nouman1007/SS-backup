import boto3
import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_account_from_budget(account_id, budget_name):
  linked_account_ids = []
  client = boto3.client("budgets")
  response = client.describe_budget(AccountId=account_id, BudgetName=budget_name)
  if(response["Budget"]["CostFilters"]["LinkedAccount"]):
    linked_account_ids = response["Budget"]["CostFilters"]["LinkedAccount"]
  return linked_account_ids

def check_and_alert_linked_accounts(linked_account_ids, account_list,dest_org_id,sns_topic):
  org_client = boto3.client("organizations")
  for linked_account in linked_account_ids :
    if linked_account in account_list:
      source_org_id = org_client.list_parents(ChildId=linked_account)[
          "Parents"][0]["Id"] # to get Organization Unit ID
      logger.debug("Source-Org:{}".format(source_org_id))
      if dest_org_id:
        logger.debug("Destination-Org:{}".format(dest_org_id))
        if source_org_id != dest_org_id:
          response = org_client.move_account(
              AccountId=linked_account,
              SourceParentId=source_org_id,
              DestinationParentId=dest_org_id
          )
          logger.debug("Response: {}".format(response))

          org = org_client.describe_organizational_unit(OrganizationalUnitId=source_org_id)
          source_org_name = org['OrganizationalUnit']['Name']
          org = org_client.describe_organizational_unit(OrganizationalUnitId=dest_org_id)
          dest_org_name = org['OrganizationalUnit']['Name']
          
          sns_client = boto3.client("sns")
          message = "Budget Threshold reached for account {}, the account has been moved from {} OU to the {} OU to prevent incurring additional charges".format(
              linked_account, source_org_name, dest_org_name)
          subject = "Budget Control Solution action for account {}".format(
              linked_account)
          sns_response = sns_client.publish(
              TopicArn=sns_topic,
              Message=message,
              Subject=subject
          )
          logger.debug("Response: {}".format(sns_response))

def process_budget_event(account_id, budget_config, dest_org_id, sns_topic, account_list):
  config_map = budget_config.split("#")
  if config_map:
    alert_type_config = config_map[3]
    budget_name_config = config_map[0]
    if alert_type_config:
      logger.debug("Alert Type Config:{}".format(alert_type_config))
      budget_name = budget_name_config.split(":")[1].strip()
      alert_type = alert_type_config.split(":")[1].strip()
      logger.debug("Alert Type:{}".format(alert_type))
      if alert_type and alert_type in ["FORECASTED", "ACTUAL"]:
        linked_account_ids = get_account_from_budget(account_id,budget_name)
        logger.debug("LinkedAccount IDs:{}".format(linked_account_ids))
        check_and_alert_linked_accounts(linked_account_ids, account_list,dest_org_id,sns_topic)
  
def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.debug("Received:{}".format(event))
    status_code = "200"
    try:
      sns_topic = os.environ["SNS_TOPIC_ARN"]
      dest_org_id = os.environ["QUARANTINE_OU"]
      account_list = os.environ["ACCOUNT_IDS"]
      message = event['Records'][0]['Sns']['Message']
      logger.debug("From SNS: " + message)

      details = message.replace("\n","#")
      logger.debug(details)
      budget_details = details.split("##")
      account_id = ((budget_details[0]).split("#")[1]).split(" ")[2]
      logger.debug("Account id:{}".format(account_id))
      budget_config = budget_details[3]
      logger.debug("BudgetDetails:{}".format(budget_config))
      process_budget_event(account_id, budget_config, dest_org_id, sns_topic,account_list)
    except Exception as e:
        logger.error(e)
        status_code=500
    return {
        'statusCode': status_code,
        'body': json.dumps('Processed the EventBridge event')
    }


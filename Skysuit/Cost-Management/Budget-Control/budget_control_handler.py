import boto3
import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_budget_event(account_id, budget_config, dest_org_id, sns_topic):
  config_map = budget_config.split("#")
  if config_map:
    alert_type_config = config_map[3]
    if alert_type_config:
      logger.debug("Alert Type Config:{}".format(alert_type_config))
      alert_type = alert_type_config.split(":")[1].strip()
      logger.debug("Alert Type:{}".format(alert_type))
      if alert_type and alert_type in ["FORECASTED", "ACTUAL"]:
        org_client = boto3.client("organizations")
        source_org_id = org_client.list_parents(ChildId=account_id)[
            "Parents"][0]["Id"]
        logger.debug("Source-Org:{}".format(source_org_id))
        if dest_org_id:
          print(dest_org_id)
          if source_org_id != dest_org_id:
            response = org_client.move_account(
                AccountId=account_id,
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
                account_id, source_org_name, dest_org_name)
            message = "Budget Threshold reached for account {}, the account has been moved from {} OU to the {} OU to prevent incurring additional charges".format(
                account_id, source_org_name, dest_org_name)

            subject = "Budget Control Solution action for account {}".format(
                account_id)
            sns_response = sns_client.publish(
                TopicArn=sns_topic,
                Message=message,
                Subject=subject
            )
            logger.debug("Response: {}".format(sns_response))


def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.debug("Received:{}".format(event))
    status_code = "200"
    try:
      sns_topic = os.environ["SNS_TOPIC_ARN"]
      dest_org_id = os.environ["QUARANTINE_OU"]
      account_id = event["account"]
      
      logger.debug("Account id:{}".format(account_id))
      details = event["detail"]["message"]
      budget_config = details.split("##")[3]
      logger.debug("BudgetDetails:{}".format(budget_config))
      process_budget_event(account_id, budget_config, dest_org_id, sns_topic)
    except Exception as e:
        logger.error(e)
        status_code=500
    return {
        'statusCode': status_code,
        'body': json.dumps('Processed the EventBridge event')
    }

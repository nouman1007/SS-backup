import logging
import boto3
import json
import datetime
import operator
import botocore
import os


findings_severity = os.environ.get('findingseverity', 'High')
loglevel = os.environ.get('loglevel', 'INFO')

logger = logging.getLogger()
logger.setLevel(loglevel)

# Create the clients outside of the handler.
inspector_client = boto3.client('inspector')
sns = boto3.client('sns')
sts  = boto3.client('sts')


#==================================================
# Default handler
#
# Inputs:
#     - SNS message payload that includes assessment run ARN
#
# Outputs:
#     - SNS message with run details
#==================================================

def lambda_handler(event, context):
    try:
        #set log output to terminal when in debug mode
        if __debug__:
            print ('Debug ON')
            ch = logging.StreamHandler()
            logger.addHandler(ch)
        
        logger.info(f"event: {event}")
        

        # extract the message that Inspector sent via SNS
        message = event['Records'][0]['Sns']['Message']

        assessment_run_arn = json.loads(message)['run']
        
        response = inspector_client.describe_assessment_runs(assessmentRunArns=[assessment_run_arn])

        rundetails = response["assessmentRuns"][0]
        logger.debug(f"Rundetails: {rundetails}")

        findingscount = rundetails['findingCounts'][findings_severity]
        
        summary = f"{findingscount} \"{findings_severity}\" severity findings found in AWS inspector assessment run  {assessment_run_arn}"
        messageBody = summary
        logger.info(summary)

        if findingscount >= 0:  #if there are finding at the level expected, prepare and send an SNS notification
            logger.debug("Prepare SNS message")

            #get account, region and assessment run and send SNS message
            accountnum = sts.get_caller_identity().get('Account')
            region = sts.meta.region_name
            snsTopicArn = os.environ.get('findingsNotificationTopicArn')

            #prepare message for SNS 
            dashboardurl="https://console.aws.amazon.com/inspector/"
            subject = f"{findingscount} {findings_severity} serverity inspector findings in account {accountnum} region: {region}"[:100] # truncate @ 100 chars, SNS subject limit
            messageBody = f"\n\n{subject} \n\nDetails:\n\nInspector assessment run arn:\n    {assessment_run_arn} \nAccount Number:\n    {accountnum} \nRegion:\n    {region} \nInspector dashboard\n    {dashboardurl}\n\n"
            messageBody = f"{messageBody}\n\n Run details:\n    Run Completed at: {rundetails['completedAt']}\n    Run Duration: {rundetails['durationInSeconds']} Secs\n"
            messageBody = messageBody + f"    Finding counts: {rundetails['findingCounts']}\n"
            messageBody = messageBody + f"\n\n\n"

            response = sns.publish(
               TopicArn = snsTopicArn,
               Message = messageBody,
                Subject = subject
            )
            logger.debug(response)

        else:
            logger.info(f"No {findings_severity} finding found in assessment run {assessment_run_arn}")


        logger.info(f"Assessment findings notification completed")
        return messageBody
    
    except Exception as e:
        logger.exception(e)
        raise


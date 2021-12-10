#####################################################################################
# The main function of this lambda function is to Set the retention period of       #                                                                                 #
# CloudWatch logs.                                                                  #        
#                                                                                   #
#                                                                                   #
#####################################################################################
from crhelper import CfnResource
import boto3
import os
import uuid
import time
import datetime
import asyncio
import json
import logging
from botocore.client import ClientError

# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

HELPER = CfnResource()

# Const Class Defined to received Paramter Values through CloudFormation Custom Resource Properties
class Const():
    KEY_RESOURCE_PROPERTIES = "ResourceProperties"
    KEY_RETENTION_PERIOD    = "cw_logs_retention"
    
@HELPER.create
@HELPER.update
def create(event, context):
    """
    Entry point for all processing. Load the global_vars
    :return: A dictionary of tagging status
    :rtype: json
    """
    logger.info('In Main Lambda Handler.')
    
    #local Veriable
    retention_period = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_RETENTION_PERIOD])
    
    # global_vars = set_global_vars(dest_bkt )
    global_vars = set_global_vars(retention_period)

    resp_data = {"status": False, "error_message" : '' }
    if not global_vars.get('status'):
        logger.error('ERROR: {0}'.format( global_vars.get('error_message') ) )
        resp_data['error_message'] = global_vars.get('error_message')
        return resp_data

    # print (resp_data)

    lgs = get_cloudwatch_log_groups(global_vars)
    if not lgs.get('status'):
        logger.error(f"Unable to get list of cloudwatch Logs.")
        resp_data['error_message'] = lgs.get('error_message')
        return resp_data

    # print(lgs)

    f_lgs = filter_logs_to_export(global_vars, lgs)
    if not (f_lgs.get('status') or f_lgs.get('log_groups')):
        err = f"There are no log group matching the filter or Unable to get a filtered list of cloudwatch Logs."
        logger.error( err )
        resp_data['error_message'] = f"{err} ERROR:{f_lgs.get('error_message')}"
        resp_data['lgs'] = {'cw_logs_to_export':global_vars.get('cw_logs_to_export'), 'filtered_logs':f_lgs}
        return resp_data

    print(f_lgs.get('log_groups'))

    # # TODO: This can be a step function (or) async 'ed
    # resp_data['export_tasks'] = []
    # #loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    
    # Lets being the archving/export process
    for lg in f_lgs.get('log_groups'):
        # resp = loop.run_until_complete( export_cw_logs_to_s3( global_vars, lg.get('logGroupName'),lg.get('retentionInDays'), global_vars.get('log_dest_bkt')) )
        # resp = loop.run_until_complete( set_retention_policy( lg.get('logGroupName')))
        set_retention_policy( global_vars, lg.get('logGroupName'))
        # resp = loop.run_until_complete( delete_retention_policy( lg.get('logGroupName')))
        # print(resp)
        # resp_data['export_tasks'].append(resp)

    # loop.close()
    #If the execution made it through here, no errors in triggering the export tasks. Set to True.
    resp_data['status'] = True
    return resp_data


def set_global_vars(retention ):
    """
    Set the Global Variables
    If User provides different values, override defaults
    This function returns the AWS account number
    :return: global_vars
    :rtype: dict
    """
    logger.info('In Setting Global Variables')
    
    global_vars = {"status": False}
    try:
        # global_vars["sns_topic_name"]           = 'cloud-watch-export-test-v' # os.environ.get("sns_topic_name")
        # global_vars["owner_email"]              = 'nshafiq@enquizit.com' # os.environ.get("owner_email")                # owner_email
        # global_vars["log_dest_bkt"]             = 'eq-v2-522955560990-us-east-1'  #os.environ.get("Dest_Bucket_Name")           # dest_bkt
        global_vars["retention_in_days"]        = int(retention)
        global_vars["time_out"]                 = 300
        global_vars["tsk_back_off"]             = 2
        global_vars["status"]                   = True
    except Exception as e:
        logger.error("Unable to set Global Environment variables. Exiting")
        global_vars["error_message"]            = str(e)
    return global_vars



def get_cloudwatch_log_groups(global_vars):
    """
    Get the list of Cloudwatch Log groups
    :param global_vars: The list of global variables
    :param type: json
    :return: resp_data Return a dictionary of data, includes list of 'log_groups'
    :rtype: json
    """
    logger.info('In Getting All Cloudwatch logs')
    resp_data = {'status': False, 'log_groups':[], 'error_message': ''}
    client = boto3.client('logs')
    try:
        # Lets get all the logs
        resp = client.describe_log_groups( limit = 50 )
        resp_data['log_groups'].extend( resp.get('logGroups') )
        # Check if the results are paginated
        if resp.get('nextToken'):
            while True:
                resp = client.describe_log_groups( nextToken = resp.get('nextToken'), limit = 50 )
                resp_data['log_groups'].extend( resp.get('logGroups') )
                # Check & Break, if the results are no longer paginated
                if not resp.get('nextToken'):
                    break
        resp_data['status'] = True
    except Exception as e:
        resp_data['error_message'] = str(e)
    return resp_data


def filter_logs_to_export(global_vars, lgs):
    """
    Get a list of log groups to export by applying filter
    :param global_vars: The list of global variables
    :param type: json
    :param lgs: The list of CloudWatch Log Groups
    :param type: json
    :return: resp_data Return a dictionary of data, includes list of filtered 'log_groups'
    :rtype: json
    """
    logger.info('In Filtering the cloudwatch Logs')
    resp_data = {'status': False, 'log_groups':[], 'error_message': ''}
    # Lets filter for the logs of interest
    for lg in lgs.get('log_groups'):
        if not 'retentionInDays' in lg:
        # if 'retentionInDays' in lg:
            resp_data['log_groups'].append(lg)
            resp_data['status'] = True
    return resp_data

# async def set_retention_policy(lg_groups):
def set_retention_policy(global_vars,lg_groups):

    logger.info('In Setting log groups retention policy')
    resp_data = {'status': False,  'error_message': ''}
    client = boto3.client('logs')
    try:
        response = client.put_retention_policy(
            logGroupName= lg_groups,
            retentionInDays= global_vars.get('retention_in_days')
        )

        resp_data['status'] = True
    except Exception as e:
        resp_data['error_message'] = str(e)
    return resp_data


# async def delete_retention_policy(lg_groups):
def delete_retention_policy(lg_groups):

    logger.info('In removing or setting back Neverexplire log group retention policy')
    resp_data = {'status': False,  'error_message': ''}
    client = boto3.client('logs')
    try:
        response = client.delete_retention_policy(
            logGroupName= lg_groups
        )

        resp_data['status'] = True
    except Exception as e:
        resp_data['error_message'] = str(e)
    return resp_data


# print (response)


# def handler(event, context):



    # """
    # Entry point for all processing. Load the global_vars
    # :return: A dictionary of tagging status
    # :rtype: json
    # """
    # logger.info('In Main Lambda Handler.')
    
    # # Variables 
    # # dest_bkt = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_DESTINATION_BUCKET])
    
    
    
    # # global_vars = set_global_vars(dest_bkt )
    # global_vars = set_global_vars( )

    # resp_data = {"status": False, "error_message" : '' }

    # if not global_vars.get('status'):
        # logger.error('ERROR: {0}'.format( global_vars.get('error_message') ) )
        # resp_data['error_message'] = global_vars.get('error_message')
        # return resp_data

    # lgs = get_cloudwatch_log_groups(global_vars)
    # if not lgs.get('status'):
        # logger.error(f"Unable to get list of cloudwatch Logs.")
        # resp_data['error_message'] = lgs.get('error_message')
        # return resp_data

    # f_lgs = filter_logs_to_export(global_vars, lgs)
    # if not (f_lgs.get('status') or f_lgs.get('log_groups')):
        # err = f"There are no log group matching the filter or Unable to get a filtered list of cloudwatch Logs."
        # logger.error( err )
        # resp_data['error_message'] = f"{err} ERROR:{f_lgs.get('error_message')}"
        # resp_data['lgs'] = {'cw_logs_to_export':global_vars.get('cw_logs_to_export'), 'filtered_logs':f_lgs}
        # return resp_data

    # # TODO: This can be a step function (or) async 'ed
    # resp_data['export_tasks'] = []
    # #loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    
    # # Lets being the archving/export process
    # for lg in f_lgs.get('log_groups'):
        # resp = loop.run_until_complete( export_cw_logs_to_s3( global_vars, lg.get('logGroupName'),lg.get('retentionInDays'), global_vars.get('log_dest_bkt')) )
        # print(resp)
        # resp_data['export_tasks'].append(resp)
    # loop.close()
    # # If the execution made it through here, no errors in triggering the export tasks. Set to True.
    # resp_data['status'] = True
    # return resp_data


def handler(event, context):
    HELPER(event, context)
  
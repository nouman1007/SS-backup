#####################################################################################
# The main function of this lambda function is to Set the retention period of       #                                                                                 #
# CloudWatch logs.                                                                  #        
#                                                                                   #
#                                                                                   #
#####################################################################################
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


def handler(event, context):

    """
    Entry point for all processing. Load the global_vars
    :return: A dictionary of tagging status
    :rtype: json
    """
    logger.info('In Main Lambda Handler.')
    
    global_vars = set_global_vars() 

    print(global_vars)
    try:
        logger.info(event)
    
        if __debug__:  # setting logger to log in console when debugging
            print ('Debug ON')
            ch = logging.StreamHandler()
            logger.addHandler(ch)
        
        resp_data = manage_cw_logs_retention_in_org(global_vars)


        return resp_data
    except Exception as e:
        logger.error('Error setting budget: ' + str(e ))
        raise e




def set_global_vars ():
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
        global_vars["ROLE_NAME"]                = os.environ.get("assume_role_name")
        global_vars["OU_Id"]                    = os.environ.get("OU_ID") #'ou-hlvo-7vgmf82j'
        global_vars["retention_in_days"]        = int (os.environ.get("cw_logs_retention")) #int(retention)
        global_vars["status"]                   = True
    except Exception as e:
        logger.error("Unable to set Global Environment variables. Exiting")
        global_vars["error_message"]            = str(e)
    return global_vars



def get_active_account_list(global_vars):   # todo: implement nextoken
    #     """
    #   This function returns list of active accounts
    # """
    client = boto3.client('organizations')
    resAccounts = client.list_accounts_for_parent(ParentId= global_vars.get('OU_Id'))  #Todo: implement next token mechanism  
    Accounts = resAccounts["Accounts"]
    while "NextToken" in resAccounts:
        resAccounts = client.list_accounts_for_parent(ParentId= global_vars.get('OU_Id'), NextToken=resAccounts["NextToken"])
        Accounts.extend(resAccounts["Accounts"])
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
    return Accounts


def  manage_cw_logs_retention_in_org(global_vars_):
    """
        CRUD for  budgets
        RetStatus = ["account": {"id: <account number>", "status": "success/fail", "info": "error, warning"}, ]
    """
    RetStatus = []
    # Get list of accountgs
    Accounts = get_active_account_list(global_vars_)

    # This loop interates over  the availabel active accounts
    
    for Account in Accounts:   
        # address error handling per account. log error and move on to the next account , finish operation
        AccountID =str(Account["Id"])
        Status = {"accountid": AccountID, "accountname": Account["Name"], "status": "started", "info": ""}
        try:
            
            manage_cw_logs_retention_in_account(Account, global_vars_)
            Status["status"] = "success"
        except Exception as e:
            logger.error (f"Error performing  in Account {AccountID}. " +  str(e))
            Status["status"] = "error"
            Status["info"] = str(e)
        
        RetStatus.append(Status)
    

    return RetStatus
    
    

def manage_cw_logs_retention_in_account(account_, global_vars):
    AccountID =str(account_["Id"])

    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.
    # Roles in each child accounts is created with role name "arn:aws:iam::"+str(Accounts[countid])+":role/Role_Billing_Alarm"
    # RoleArn= "arn:aws:iam::" + str(AccountId)+ ":role/Role_Billing_Alarm",
    sts_client = boto3.client('sts')
    assumed_role_object=sts_client.assume_role(
                            RoleArn= f"arn:aws:iam::{AccountID}:role/{global_vars.get('ROLE_NAME')}",    # Interates over accounts and grap the cross-account role permission to create budget
                            RoleSessionName=f"BillingAlertSession{AccountID}"                             
                        )

    # From the response that contains the assumed role, get the temporary 
    # credentials that can be used to make subsequent API calls
    credentials=assumed_role_object['Credentials']

    # Use the temporary credentials that AssumeRole returns to make a 
    # connection to Amazon Cloudwatch Logs
    cw_logs_client=boto3.client('logs',aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],aws_session_token=credentials['SessionToken'])



    resp_data = {"status": False, "error_message" : '' }
    if not global_vars.get('status'):
        logger.error('ERROR: {0}'.format( global_vars.get('error_message') ) )
        resp_data['error_message'] = global_vars.get('error_message')
        return resp_data


    lgs = get_cloudwatch_log_groups(global_vars, cw_logs_client)
    if not lgs.get('status'):
        logger.error(f"Unable to get list of cloudwatch Logs.")
        resp_data['error_message'] = lgs.get('error_message')
        return resp_data


    f_lgs = filter_logs_to_export(global_vars, lgs)
    if not (f_lgs.get('status') or f_lgs.get('log_groups')):
        err = f"There are no log group matching the filter or Unable to get a filtered list of cloudwatch Logs."
        logger.error( err )
        resp_data['error_message'] = f"{err} ERROR:{f_lgs.get('error_message')}"
        return resp_data

    
    # Lets being setting retention policy
    for lg in f_lgs.get('log_groups'):
        set_retention_policy( global_vars, lg.get('logGroupName'), cw_logs_client)

    resp_data['status'] = True
    
    return resp_data
    



def get_cloudwatch_log_groups(global_vars, cw_logs_client_):
    """
    Get the list of Cloudwatch Log groups
    :param global_vars: The list of global variables
    :param type: json
    :return: resp_data Return a dictionary of data, includes list of 'log_groups'
    :rtype: json
    """
    logger.info('In Getting All Cloudwatch logs')
    resp_data = {'status': False, 'log_groups':[], 'error_message': ''}
    # client = boto3.client('logs')
    try:
        # Lets get all the logs
        resp = cw_logs_client_.describe_log_groups( limit = 50 )
        resp_data['log_groups'].extend( resp.get('logGroups') )
        # Check if the results are paginated
        if resp.get('nextToken'):
            while True:
                resp = cw_logs_client_.describe_log_groups( nextToken = resp.get('nextToken'), limit = 50 )
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
    :return: resp_data Return a dictionary of data
    :rtype: json
    """
    logger.info('In Filtering the cloudwatch Logs')
    resp_data = {'status': False, 'log_groups':[], 'error_message': ''}
    # Lets filter for the logs of interest
    for lg in lgs.get('log_groups'):
        if not 'retentionInDays' in lg:
            resp_data['log_groups'].append(lg)
            resp_data['status'] = True
    return resp_data



def set_retention_policy(global_vars,lg_groups, cw_logs_client_):

    logger.info('In Setting log groups retention policy')
    resp_data = {'status': False,  'error_message': ''}
    # client = boto3.client('logs')
    try:
        response = cw_logs_client_.put_retention_policy(
            logGroupName= lg_groups,
            retentionInDays= global_vars.get('retention_in_days')
        )

        resp_data['status'] = True
    except Exception as e:
        resp_data['error_message'] = str(e)
    return resp_data
  
  

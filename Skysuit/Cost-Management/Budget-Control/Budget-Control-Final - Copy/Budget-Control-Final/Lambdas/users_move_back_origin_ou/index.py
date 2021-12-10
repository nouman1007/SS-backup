#####################################################################################
# The main function of this lambda function is to Set the retention period of       #                                                                                 #
# CloudWatch logs.                                                                  #        
#                                                                                   #
#                                                                                   #
#####################################################################################
import boto3
import os
import json
import logging
# from botocore.client import ClientError

# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):

    # """
    # Entry point for all processing.
    # :return: A dictionary of tagging status
    # :rtype: json
    # """
    logger.info('In Main Lambda Handler.')
    
    Source_org_id = os.environ.get("OU_ID") #'ou-hlvo-7vgmf82j''ou-hlvo-7vgmf82j'
    acct_list = get_active_account_list(Source_org_id)

    Account_Ids=[]
    for acct in acct_list:
        print(acct)
        Account_Ids.append(acct['Id'])
    print(Account_Ids)



    for act in Account_Ids:
        test_1 = List_tags(act)
        tst=test_1['Tags']
        Keys = []
        tags = {}
        for ts in tst:
            tags[ts['Key']] = ts['Value']
            Keys.append(ts['Key'])

        if tags.get('KeepQuarantine') == 'False':
            Un_tag(act,Keys)
            Move_Account(act, Source_org_id, tags.get('Origin-OU-ID'))
            print(tags.get('Origin-OU-ID'))
        else:
            print('try again man')

    
    # global_vars = set_global_vars() 

    # print(global_vars)
    # try:
        # logger.info(event)
    
        # if __debug__:  # setting logger to log in console when debugging
            # print ('Debug ON')
            # ch = logging.StreamHandler()
            # logger.addHandler(ch)
        
        # resp_data = manage_cw_logs_retention_in_org(global_vars)


        # return resp_data
    # except Exception as e:
        # logger.error('Error setting budget: ' + str(e ))
        # raise e
  


def List_tags(resource_id):

    client = boto3.client('organizations')
    response = client.list_tags_for_resource(
    ResourceId=resource_id,
    # NextToken='string'
    )
    return response
    
    
def Un_tag(Account_Id,Key):

    client = boto3.client('organizations')

    response = client.untag_resource(
    ResourceId= Account_Id,
    TagKeys=Key
    )
    return response
    
def get_active_account_list(source_org_id):   # todo: implement nextoken
    #     """
    #   This function returns list of active accounts
    # """
    client = boto3.client('organizations')
    # resAccounts = client.list_accounts_for_parent(ParentId= ouid)  #Todo: implement next token mechanism  
    # source_org_id = client.list_parents(ChildId=account_id)["Parents"][0]["Id"]
    resAccounts = client.list_accounts_for_parent(ParentId= source_org_id)  #Todo: implement next token mechanism  
    Accounts = resAccounts["Accounts"]
    while "NextToken" in resAccounts:
        resAccounts = client.list_accounts_for_parent(ParentId= source_org_id, NextToken=resAccounts["NextToken"])
        Accounts.extend(resAccounts["Accounts"])

    # temporary
    # Accounts = [{
    #         "Id": "834800198471",
    #         "Arn": "string",
    #         "Email": "hiruytyy@yahoo.com",
    #         "Name": "string",
    #         "Status": "ACTIVE",
    #         "JoinedMethod": "INVITED"
    # }
    #         ]
    return Accounts
    
    
def Move_Account(Account_id, Source_org_id, Dest_org_id):

    org_client = boto3.client("organizations")

    response = org_client.move_account(
    AccountId=Account_id,
    SourceParentId=Source_org_id,
    DestinationParentId=Dest_org_id
    )
    return response




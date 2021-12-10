from crhelper import CfnResource
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


HELPER = CfnResource()
POLICY_CLIENT = boto3.client('organizations')


class Const():
    KEY_RESOURCE_PROPERTIES = "ResourceProperties"
    KEY_POLICY_NAME = "PolicyName"
    KEY_POLICY_DOC = "PolicyDoc"
    KEY_POLICY_TYPE = "PolicyType"
    KEY_POLICY_DES = "Description"

    

@HELPER.create
@HELPER.update
def create(event, context):
    
    logger.info('In Main Lambda Handler.')
        
    # Local variables
    policy_name     = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_POLICY_NAME])
    policy_doc      = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_POLICY_DOC])
    policy_type     = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_POLICY_TYPE])
    policy_des      = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_POLICY_DES])
    
    #Function definations.
    create_policy(policy_doc ,policy_des ,policy_name ,policy_type )
    
    #Function to Create Service Control Policy.    
def create_policy(policyjson , policydescription, policyname ,policytype ):
    """
    This fucntion Create Service Control Policy.
    """
    logger.info("In create")
    
    try:
        resp = POLICY_CLIENT.create_policy(
            Content=json.dumps(policyjson),
            Description=policydescription,
            Name=policyname,
            Type=policytype)
            
    except Exception as err:
        logger.error("send(..) failed to Create the Policy : " + str(err))
        raise Exception(err)
    logger.info("Policy has been created Successfully")    
    return resp['Policy']['PolicySummary']['Arn']
    
def handler(event, context):
    HELPER(event, context)
from crhelper import CfnResource
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


HELPER = CfnResource()
ASSESSMENT_CLIENT = boto3.client('inspector')


class Const():
    KEY_ASSESSMENT_TEMPLATE_ARN = "assessment_template_arn"
    KEY_RESOURCE_PROPERTIES = "ResourceProperties"
    

@HELPER.create
@HELPER.update
def create(event, context):
    
    logger.info('In Main Lambda Handler.')
        
    # variables
    
    #Function definations.
    assessment_run((event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_ASSESSMENT_TEMPLATE_ARN]))                       #  Assessment Template Arn
        
        
def assessment_run(arn):
    """
    This fucntion run the assessment Template.
    """
    logger.info("In Start assessment template")
    
    try:
        ASSESSMENT_CLIENT.start_assessment_run( assessmentTemplateArn = arn )

    except Exception as err:
        logger.error("send(..) failed to run the assessment template : " + str(err))
        raise Exception(err)
    logger.info("Assessment template start run")    
    
    
def handler(event, context):
    HELPER(event, context)
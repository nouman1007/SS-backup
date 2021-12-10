from crhelper import CfnResource
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


HELPER = CfnResource()
GLUE_CLIENT = boto3.client('glue')


class Const():
    KEY_CRAWLER_NAME    = "crawler_name"
    KEY_RESOURCE_PROPERTIES = "ResourceProperties"
    
# reviewnotes: there is no handler for delete? is this intentinal. is there a roll back equivalent for crawler initialize?
# reviewnotes: the only way to invoke an update is by giving a new crawler name. in that case what happens to the old crawler? does it not have to be stopped?

@HELPER.create
@HELPER.update
def create(event, context):
    
    logger.info('In Main Lambda Handler.')
    
    
    # variables
    glue_crawler_name = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_CRAWLER_NAME])                    #  Crawler name
    
    #Function definations.
    crawler_intializer(glue_crawler_name) 
        
        
def crawler_intializer(crawler):
    """
    This fucntion Initializing the crawler.
    """
    logger.info("In crawler_intializer")
    
    try:
        GLUE_CLIENT.start_crawler( Name = crawler )

    except Exception as err:
        logger.error("send(..) failed to Initialize Crawler : " + str(err))
        raise Exception(err)
    logger.info("Crawler Initialized!")    
    
    
def handler(event, context):
    HELPER(event, context)
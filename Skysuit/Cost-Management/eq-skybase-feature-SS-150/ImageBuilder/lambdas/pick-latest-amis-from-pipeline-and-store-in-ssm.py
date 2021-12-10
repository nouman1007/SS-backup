import json
import boto3
import logging
import os
from operator import itemgetter


logger = logging.getLogger()
logger.setLevel(logging.INFO)


imagebuilder = boto3.client('imagebuilder')
ssm = boto3.client('ssm')

def handler(event, context):
    
    logger.info("--In lambda Hnadler---")
    
    arn_windows_pipeline = os.environ.get('windows_pipeline_arn')
    arn_centos_pipeline = os.environ.get('centos_pipeline_arn')
    
    windows_parameter_name = os.environ.get('windows_parameter')
    centos_parameter_name = os.environ.get('centos_parameter')
    
    window_ami = get_latest_windows_AMI_from_pipeline(arn_windows_pipeline)   
    centos_ami = get_latest_centos_AMI_from_pipeline(arn_centos_pipeline)   

    update_window_ssm_parameter(window_ami, windows_parameter_name)
    update_centos_ssm_parameter(centos_ami, centos_parameter_name)
    
    
def get_latest_windows_AMI_from_pipeline(arn_windows_pipeline):
    
    logger.info("---In getting latest windows ami from pipeline---")
    
    responce_collector = []
    response = imagebuilder.list_image_pipeline_images(imagePipelineArn=arn_windows_pipeline)
    
    responce_collector += response['imageSummaryList']
    while('nextToken' in response.keys()):
        response = imagebuilder.list_image_pipeline_images(imagePipelineArn=arn_windows_pipeline, nextToken=response["nextToken"])
        responce_collector += response['imageSummaryList']
    
    image_details = sorted(responce_collector, key=itemgetter('dateCreated'), reverse=True)
    ami_id = image_details[0]['outputResources']
    image_id = ami_id['amis']
    latest_ami = [ sub['image'] for sub in image_id ]
    window_ami = ''.join(latest_ami)
    
    return window_ami    
    
    
def get_latest_centos_AMI_from_pipeline(arn_centos_pipeline):
    
    logger.info("---In getting latest centos ami from pipeline---")    
    responce_collector = []
    response = imagebuilder.list_image_pipeline_images(imagePipelineArn=arn_centos_pipeline)
    
    responce_collector += response['imageSummaryList']
    while('nextToken' in response.keys()):
        response = imagebuilder.list_image_pipeline_images(imagePipelineArn=arn_centos_pipeline, nextToken=response["nextToken"])
        responce_collector += response['imageSummaryList']
    
    image_details = sorted(responce_collector, key=itemgetter('dateCreated'), reverse=True)
    ami_id = image_details[0]['outputResources']
    image_id = ami_id['amis']
    latest_ami = [ sub['image'] for sub in image_id ]
    centos_ami = ''.join(latest_ami)
    
    return centos_ami

def update_window_ssm_parameter(window_ami, windows_parameter_name):
    
    logger.info("---In updating window ssm parameter store---")
    
    response = ssm.put_parameter(
        Name=windows_parameter_name,
        Description='parameter store for windows ami',
        Value=window_ami,
        Type= 'String',
        Overwrite=True
    )
    
def update_centos_ssm_parameter(centos_ami, centos_parameter_name):
    
    logger.info("---In updating centos ssm parameter store---")
    response = ssm.put_parameter(
        Name=centos_parameter_name,
        Description='parameter store for centos ami',
        Value=centos_ami,
        Type= 'String',
        Overwrite=True
    )
import json
import boto3
import logging 
import time
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


REGION = '<region selected>'  
INSTANCE_TYPE = 'm3.medium'            
                    
ec2 = boto3.client('ec2', region_name=REGION)
cfn = boto3.client('cloudformation')


def handler(event,context):
    image_id = event['ami']
    instance_id = event['instanceID']
    
    Window_Parent_AMI=os.environ['Window_Parent_AMI']
    Window_Stig_Component=os.environ['Window_Stig_Component']
    Window_Reboot_Component=os.environ['Window_Reboot_Component']
    Window_Recipe_Name=os.environ['Window_Recipe_Name']
    Window_Config=os.environ['Window_Config_Name']
    Window_Pipeline=os.environ['Window_Pipeline_Name']
    Window_Distribution=os.environ['Window_Distribution_Name']
          
    Centos_compoenent=os.environ['Centos_Component']
    Centos_Recipe_Name=os.environ['Centos_Recipe_Name']
    Centos_Config=os.environ['Centos_Config_Name']
    Centos_Pipeline=os.environ['Centos_Pipeline_Name']
    Centos_Distribution=os.environ['CentosDistribution']
    
    Stack_Name=os.environ['Stack_Name']
    NetworkStack=os.environ['NeworkStack']
    
    terminate_instance(instance_id)
    create_cloudformation_stack(NetworkStack, image_id,Stack_Name, Window_Parent_AMI, Window_Stig_Component, Window_Reboot_Component, Window_Recipe_Name, Window_Config, Window_Pipeline, Window_Distribution, Centos_compoenent, Centos_Recipe_Name, Centos_Config, Centos_Pipeline, Centos_Distribution)
    
    
    
def terminate_instance(instance_id):
    
    logger.info("In terminate Instance")
    
    response = ec2.terminate_instances(
        InstanceIds=[
            instance_id,
        ],
    )
     
    logger.info('Instance terminated --- out from function')
    
def create_cloudformation_stack(NetworkStack, new_image_ID, Stack_Name, Window_Parent_AMI, Window_Stig_Component, Window_Reboot_Component, Window_Recipe_Name, Window_Config, Window_Pipeline, Window_Distribution, Centos_compoenent, Centos_Recipe_Name, Centos_Config, Centos_Pipeline, Centos_Distribution):
    
    logger.info("In stack function")
    
    try:
        responce = cfn.describe_stacks(StackName = Stack_Name)
        logger.info("stack exist---updating")
        
        response = cfn.update_stack(
            StackName=Stack_Name,
            UsePreviousTemplate=True,
            Parameters=[
                {
                    'ParameterKey': 'pCentosParentImage',
                    'ParameterValue': new_image_ID
                },
                {
                    'ParameterKey': 'pWindowStigComponents',
                    'ParameterValue': True
                },
                {
                    'ParameterKey': 'pWindowParentImage',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pWindowSourceStackName',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pWindowRebootComponents',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pWindowImageRecipeName',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pWindowInfrastructureConfigurationName',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pWindowImagePipelineName',
                    'ParameterValue': True
                },
                {
                    'ParameterKey': 'pWindowDistributionConfigurationName',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pCentosComponents',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pCentosSourceStackName',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pCentosImageRecipe',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pCentosInfrastructureConfiguration',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pCentosImagePipeline',
                    'UsePreviousValue': True
                },
                {
                    'ParameterKey': 'pCentosDistributionConfiguration',
                    'UsePreviousValue': True
                }
            ]
        )
          
    except Exception as err:
        logger.info("Stack doesnot exist---creating stack")
        
        response = cfn.create_stack(
            StackName=Stack_Name,
            TemplateURL='<Copy the URL of nested_template.yaml and paste here>',
            Capabilities=['CAPABILITY_IAM','CAPABILITY_AUTO_EXPAND'],
            Parameters=[
                {
                    'ParameterKey': 'pWindowStigComponents',
                    'ParameterValue': Window_Stig_Component,
                },
                {
                    'ParameterKey': 'pWindowParentImage',
                    'ParameterValue': Window_Parent_AMI,
                },
                {
                    'ParameterKey': 'pWindowSourceStackName',
                    'ParameterValue': NetworkStack,
                },
                {
                    'ParameterKey': 'pWindowRebootComponents',
                    'ParameterValue': Window_Reboot_Component,
                },
                {
                    'ParameterKey': 'pWindowImageRecipeName',
                    'ParameterValue': Window_Recipe_Name,
                },
                {
                    'ParameterKey': 'pWindowInfrastructureConfigurationName',
                    'ParameterValue': Window_Config,
                },
                {
                    'ParameterKey': 'pWindowImagePipelineName',
                    'ParameterValue': Window_Pipeline,
                },
                {
                    'ParameterKey': 'pWindowDistributionConfigurationName',
                    'ParameterValue': Window_Distribution,
                },
                {
                    'ParameterKey': 'pCentosParentImage',
                    'ParameterValue': new_image_ID,
                },
                {
                    'ParameterKey': 'pCentosImagePipeline',
                    'ParameterValue': Centos_Pipeline,
                },
                {
                    'ParameterKey': 'pCentosDistributionConfiguration',
                    'ParameterValue': Centos_Distribution,
                },
                {
                    'ParameterKey': 'pCentosComponents',
                    'ParameterValue': Centos_compoenent,
                },
                {
                    'ParameterKey': 'pCentosSourceStackName',
                    'ParameterValue': NetworkStack
                },
                {
                    'ParameterKey': 'pCentosImageRecipe',
                    'ParameterValue': Centos_Recipe_Name,
                },
                {
                    'ParameterKey': 'pCentosInfrastructureConfiguration',
                    'ParameterValue': Centos_Config
                } 
            ]
        )
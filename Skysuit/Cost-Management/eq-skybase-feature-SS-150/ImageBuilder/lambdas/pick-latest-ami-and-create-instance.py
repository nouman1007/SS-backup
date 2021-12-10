import json
import boto3
import logging 
import time
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


REGION = '<region selected>'  
INSTANCE_TYPE = 't2.medium'     

BUCKET = '<bucket name created>'
SCRIPT_PATH = 'script.sh'
LOCAL_PATH = '/tmp/local_script.sh'
                    
ec2 = boto3.client('ec2', region_name=REGION)
S3 = boto3.client('s3', region_name=REGION)
S3.download_file(BUCKET, SCRIPT_PATH, LOCAL_PATH)

with open(LOCAL_PATH, 'r') as f:
    script = '\n'.join(f)

    
def handler(event,context):
   
    Role_Name = os.environ['Role_Name']
    Key = os.environ['Key']
    Security_Group = os.environ['Security_Group']
    Subnet = os.environ['Subnet']
    
    latest_ami = grab_latest_image()
    instance_ID = create_ec2_instance(latest_ami,script,Role_Name, Key, Security_Group, Subnet)    
    
    
def grab_latest_image():
    
    logger.info('In grab latest image for centos')
    
    response= ec2.describe_images(Owners=['679593333241'],Filters=[{'Name': 'name', 'Values': ['CentOS Linux 7 x86_64 HVM EBS *']},{'Name': 'architecture', 'Values': ['x86_64']},{'Name': 'root-device-type', 'Values': ['ebs']},], )
    amis = sorted(response['Images'], key=lambda x: x['CreationDate'],reverse=True)
    latestAmi = amis[0]['ImageId'] 
    
    logger.info('Out from grab latest AMI')
    
    return latestAmi ami-123(latest centos, don't have ssm agent')


def create_ec2_instance(latest_ami,script,Role_Name, Key, Security_Group, Subnet):
    
    logger.info("In creating new instance")
    
    instance = ec2.run_instances( 
        ImageId=latest_ami,  
        InstanceType=INSTANCE_TYPE,
        MinCount=1, 
        MaxCount=1,
        IamInstanceProfile={
            'Name': Role_Name
        },
        KeyName= Key,
        InstanceInitiatedShutdownBehavior='terminate', 
        NetworkInterfaces=[
            {
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True,
                'DeviceIndex': 0,
                'Groups': [Security_Group],
                'SubnetId': Subnet
            }
        ],

        UserData=script
    )
    instance_id = instance['Instances'][0]['InstanceId']
    
    logger.info('Instance created --- out from function')
    return instance_id
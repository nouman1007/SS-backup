from crhelper import CfnResource
import json
import boto3
import os
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Const():
    KEY_RESOURCE_PROPERTIES = "ResourceProperties"
    KEY_IAM_INSTANCE_PROFILE_NAME = "iaminstanceprofilename"
    KEY_TAG_VALUE = "tagvalue"
    KEY_INTANCES_NAME = "instancesname"
    
HELPER = CfnResource()
ec2 = boto3.client('ec2')

@HELPER.create
@HELPER.update
def create(event, context):

    iam_instance_profile_name = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_IAM_INSTANCE_PROFILE_NAME])                            #  IAM_INSTANCE_PROFILE_NAME
    tag_value = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_TAG_VALUE])                                                            #  TAG_VALUE
    instance_name = (event[Const.KEY_RESOURCE_PROPERTIES][Const.KEY_INTANCES_NAME])                                                    #  INTANCES_NAME

    profile = ec2.describe_iam_instance_profile_associations()
    PROFILE = profile['IamInstanceProfileAssociations']

    # Grab where backup retention is 14 days so we can reduce it to 7
    instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])

    # print (instances)

    instance_ids = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
            
    print("==================start======================================")
    association_ids = []
    for association in PROFILE:
        if association['State'] == 'associated':
            for ids in instance_ids:
                print(ids)
                print(association['InstanceId'])
                if ids == association['InstanceId']:
                    print("true True")
                    association_ids.append(association['AssociationId'])
                else:
                    print("false False")
        else:
            print("Null Null")
    print (association_ids)

    if len(association_ids) == 0:
        print ("list is empty")
        iam_profile_associate(iam_instance_profile_name, instance_ids)
    else:
        dis_associate_profile(association_ids)
        iam_profile_associate(iam_instance_profile_name, instance_ids)

    # Attach_Tag(VALUE, instance_ids)
    print ("Changing tags for %d instances" % len(instance_ids))

    attach_tag(tag_value, instance_ids)
    
    
# Create an associate_profile 
def dis_associate_profile(ids):

    for dis in ids:
        dis_associate = ec2.disassociate_iam_instance_profile(
        AssociationId= dis,
    )
    print(dis_associate)
    
    
def iam_profile_associate(name, instanceid):

    for associate in instanceid:
        iam_associate = ec2.associate_iam_instance_profile(
            IamInstanceProfile={
                'Name': name,
            },
            InstanceId= associate,
        )
    print(iam_associate)
    
# Patch Group addition function
def attach_tag(value, ids):  
    ec2.create_tags(
        Resources=ids,
        Tags=[
            {
                'Key': 'Patch Group',
                'Value': value
            }
        ]
    )
        

def handler(event, context):

    try:
      HELPER(event, context)
    except Exception as err:
      logger.error("send(..) failed to create CUR report : " + str(err))
      raise Exception(err)
    logger.info('In Main Lambda Handler')
    logger.info(json.dumps(event))


    

import json
import boto3
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
          
         
organization_client = boto3.client('organizations')
         
def handler(event,context):
    
    logger.info("In main handler function")
    
    OldDays = os.environ['NumberOfDays']
    TimeLimit = int(OldDays)    

    sts_connection = boto3.client('sts')

    logger.info("Picked Master account ID")
    master_account_id = [context.invoked_function_arn.split(":")[4]]

    
    all_organization_accounts = []
    
    try:
        logger.info("API CALL TO LIST THE ACCOUNTS IN ORGANIZATION")
        response = organization_client.list_accounts()
        all_organization_accounts += response["Accounts"]
        
        while("NextToken" in response.keys()):
            response = organization_client.list_accounts(NextToken = response["NextToken"])
            all_organization_accounts += response["Accounts"]
            
    except Exception as e:
        logger.error("Failed to get account information!!! : " + str(e))  
    
    logger.info("Recieved all account IDs")
    all_organization_accounts = [org_account['Id'] for org_account in all_organization_accounts] 
    
    member_accounts= [x for x in all_organization_accounts  if x not in  master_account_id]
    
    logger.info("Started for loop to assume the role in each account one by one!")
    for m_account in member_accounts:
        arn = 'arn:aws:iam::'+m_account+':role/CrossAccountRole'
        acct_b = sts_connection.assume_role(
            RoleArn= arn,
            RoleSessionName="cross_acct_lambda"
        )
    
        ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
        SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
        SESSION_TOKEN = acct_b['Credentials']['SessionToken']
        
        logger.info("Session created with account" + m_account)
        ec2_client = boto3.client('ec2',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN,)
        
        availableVols = getAvailableVolumes(ec2_client)
        deleteVolumes(availableVols,ec2_client)
        
        
        oldSnapshots = getOldSnapshots(TimeLimit,ec2_client) 
        snapshotsToDelete = checkTagsOfOldSnaps(oldSnapshots, ec2_client)
        detach_ami(snapshotsToDelete,ec2_client)
        deleteEbsSnapshots(snapshotsToDelete,ec2_client)
        
        rds_client = boto3.client('rds',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN,)
          
        oldRdsSnapshots = getOldRdsSnapshots(TimeLimit,rds_client)
        snapshotsToDelete=checkTagsOfOldRDSSnaps(oldRdsSnapshots,m_account,rds_client)
        deleteRDSSnapshots(snapshotsToDelete,rds_client)

        oldAuroraSnapshots = getOldAurorraSnapshots(TimeLimit,rds_client)
        auroraSnapshotsToDelete=checkTagsOfAuroraOldSnaps(oldAuroraSnapshots,m_account,rds_client)
        deleteAuroraSnapshots(auroraSnapshotsToDelete,rds_client)
    
    logger.info("-----End of Deleting Resources Function-----")
    
def getAvailableVolumes(ec2_client):
    #--------------------------------------------------------------------------
    # returns list of volumes in 'available' state.
    # Parameters Description -> parametername:type:description
    #
    # availableVolList:list:It will consist of Volumes which are in available state
    #---------------------------------------------------------------------------
    
    logger.info("In getting available volumes function.")        
    availableVolList = []
    
    filterList = [{'Name': 'status', 'Values': ['available']}]
    
    response = ec2_client.describe_volumes(Filters=filterList, MaxResults=500)
    
    for v in response['Volumes']:
        availableVolList.append(v['VolumeId'])
    while('NextToken' in response):
        response = ec2_client.describe_volumes(Filters=filterList, MaxResults=500, NextToken=response['NextToken'])
        
        for v in response['Volumes']:
            availableVolList.append(v['VolumeId'])
    logger.info("Recieved all avaialable volumes/un attached volumes.")        
    return availableVolList
          
          
def deleteVolumes(availableVols,ec2_client):
    #---------------------------------------------------------------
    # Gets the list of available bvolumes from prvious function as argument
    # and delete unattched volumes by calling the delete_volume API
    #----------------------------------------------------------------------
    
    
    logger.info("In deletion of unattached volumes function.")
    for vol in availableVols:
        response = ec2_client.delete_volume(VolumeId=vol)
    logger.info("Deleted unattached volumes.")    

               
def getOldSnapshots(TimeLimit,ec2_client):
    
    #-------------------------------------------------------------------------------------------
    # returns list of snapshots which are older than "TimeLimit"
    # Parameter Description -> Parameter name: type:description 
    # oldSnapsList:List:Consist of EBS Snapshots ID which are older than "TimeLimit" argument
    # days_old:integer:number of days from snapshot created.
    #---------------------------------------------------------------------------------------------
    
    logger.info("In getting old ebs snapshots function")
    oldSnapsList = []
    
    logger.info("Api call to describe all snapshots.")    
          
    allResponse = ec2_client.describe_snapshots(OwnerIds=['self'])
    
    for snap in allResponse['Snapshots']:
        days_old = (datetime.now(timezone.utc) - snap['StartTime']).days   
        if days_old > TimeLimit: 
            oldSnapsList.append(snap['SnapshotId'])
    while('NextToken' in allResponse):
        allResponse = ec2_client.describe_snapshots(OwnerIds=['self'],NextToken=allResponse['NextToken'])
        for snap in allResponse['Snapshots']:
            days_old = (datetime.now(timezone.utc) - snap['StartTime']).days
            if days_old > TimeLimit:
                oldSnapsList.append(snap['SnapshotId'])
    logger.info("Got all the snapshots which are older than " + str(TimeLimit) + " Days!")            
    return oldSnapsList
              
def checkTagsOfOldSnaps(oldSnapshots,ec2_client):
    
    #-----------------------------------------------------------------------------------------          
    # check oldSnapshots  List with tag: DoNotDelete = True
    # Parameter Description -> Parameter name: type: description
    # snapShotsWithTag: List: All EBS Snapshots which have tag: Key: DoNotDelete, Value: True
    # snapshotsToDelete: List: Consist of EBS Snapshot Ids which don't have tag.
    #---------------------------------------------------------------------------------------
    logger.info("Now checking tha tags of Old EBS Snapshots.")          
    FILTER_CRITERIA = json.loads( os.environ.get('FILTER', '[{"Name": "tag:DoNotDelete","Values": ["True"]}]'))
    
    snapShotsWithTag = []
    snapShotsWithTagResponce = ec2_client.describe_snapshots(OwnerIds=['self'], Filters = FILTER_CRITERIA)
              
    for ids in snapShotsWithTagResponce['Snapshots']:
        snapShotsWithTag.append(ids['SnapshotId'])
    while('NextToken' in snapShotsWithTagResponce):
        response = ec2_client.describe_snapshots(OwnerIds=['self'],NextToken=snapShotsWithTagResponce['NextToken'])
        for ids in response['Snapshots']:
            snapShotsWithTag.append(ids['SnapshotId'])    
    
    logger.info("Collected all the snapshots which are about to delete. Only snapshot having tag = true will not delete.")              
    
    # snapshotsToDelete = all old snapshots - snapshots with tag true    
    snapshotsToDelete= [x for x in oldSnapshots  if x not in  snapShotsWithTag]
              
    return snapshotsToDelete

def detach_ami(snapshotsToDelete,ec2_client):
    
    #----------------------------------------------------------------------
    # check if snapshot which is about to delete is in use with any AMI.
    # Gets AMI which is attached to snapshot from snapshotsToDelete list.
    # deregister the ami.
    #------------------------------------------------------------------------
    
    logger.info("In Detaching AMI function")
    amiId=[]
              
    for snapId in snapshotsToDelete:
        response = ec2_client.describe_images(
            Filters=[
                {
                    'Name': 'block-device-mapping.snapshot-id',
                    'Values': [snapId,]
                },
            ],
            Owners=['self',],
        )
        for amis in response['Images']:
            amiId.append(amis['ImageId'])
    for i in amiId:
        response = ec2_client.deregister_image(ImageId=i)
    logger.info("Detached the AMIs. ")    
                    
def deleteEbsSnapshots(snapshotsToDelete,ec2_client):
    
    #-------------------------------------------------------
    # Deletes the EBS snapshots.
    #------------------------------------------------------
    logger.info("In deleting the old ebs snapshots function")          
    for snap in snapshotsToDelete:
        response=ec2_client.delete_snapshot(SnapshotId=snap)

              
def getOldRdsSnapshots(TimeLimit,rds_client):

    #----------------------------------------------------------
    # returns list of snapshots which are older than "NumberOfDays"
    # days_old = number of days from snapshot created.
    # oldSnapList =  List of snapshots that are older than x number of days.
    #----------------------------------------------------------
    
    logger.info("In getting OLD RDS Snapashots")
    oldSnapsList = []
              
    allResponse = rds_client.describe_db_snapshots()

    for db in allResponse["DBSnapshots"]:
        days_old = (datetime.now(timezone.utc) - db['SnapshotCreateTime']).days
        if days_old > TimeLimit:
            oldSnapsList.append(db['DBSnapshotIdentifier'])
            
    logger.info("Got all the OLD RDS Snapashots which are older than " +str(TimeLimit)+ " Days. ")
        
    return oldSnapsList          
              
def checkTagsOfOldRDSSnaps(oldRdsSnapshots,m_account,rds_client):
    
    #--------------------------------------------------------------------------------
    # snapshotsWithTagTrue =  This is list which will collect the snapshots froM oldSnapShots list having tag : DoNotDelete =  True
    # snapshotsToDelete =   This is a list which will consiste of all oladSnapshots - snapshotsWithTagTrue
    #----------------------------------------------------------------------------------
    
    logger.info("Checking tafgs of OLD RDS Snapshots. ")
    snapshotsWithTagTrue = []
    dict_test = {'Key': 'DoNotDelete', 'Value': 'True'}
 
    my_region = os.environ['AWS_REGION']

    for snapID in oldRdsSnapshots:
        ARN="arn:aws:rds:"+my_region+":"+m_account+":snapshot:"+snapID
        
        response = rds_client.list_tags_for_resource(ResourceName=ARN)
        
        if dict_test in response['TagList']:
            snapshotsWithTagTrue.append(snapID)
    logger.info("Old RDS Snapshots which are to be deleted are collected in list. ")        
              
    snapshotsToDelete= [x for x in oldRdsSnapshots  if x not in  snapshotsWithTagTrue]         
    return snapshotsToDelete

          
def deleteRDSSnapshots(snapshotsToDelete,rds_client):
    
    #---------------------------
    # Deletes the RDS snapshots!
    #---------------------------
    
    logger.info("In deletion of Old RDS Snapshots. ")
    for snap in snapshotsToDelete:
        try:
            response = rds_client.delete_db_snapshot(DBSnapshotIdentifier=snap)
        except Exception as e:
            logger.error("Unable to delete the automated RDS Snapshots")
    logger.info("Deleted old RDS Snapshots. ")

def getOldAurorraSnapshots(TimeLimit,rds_client):

    #------------------------------------------------------------------------------
    # returns list of Aurora snapshots(Manual+system) which are older than "TimeLimit"
    # days_old = number of days from snapshot created.
    # OldAuroraRdsSnapshotList =  List of snapshots that are older than "TimeLimit" number of days.
    #------------------------------------------------------------------------------
    
    OldAuroraRdsSnapshotList=[]

    allresponse = rds_client.describe_db_cluster_snapshots()
    for db in allresponse["DBClusterSnapshots"]:
        days_old = (datetime.now(timezone.utc) - db['SnapshotCreateTime']).days
        if days_old > TimeLimit:
            OldAuroraRdsSnapshotList.append(db['DBClusterSnapshotIdentifier'])
    return OldAuroraRdsSnapshotList

     
def checkTagsOfAuroraOldSnaps(oldAuroraSnapshots,m_account,rds_client):
    
    
    #--------------------------------------------------------------------------------
    # AurorasnapshotsWithTagTrue =  This is list which will collect the snapshots froM oldSnapShots list having tag : DoNotDelete =  True
    # snapshotsToDelete =   This is a list which will consiste of all oladSnapshots - snapshotsWithTagTrue
    #----------------------------------------------------------------------
    
    AurorasnapshotsWithTagTrue = []
    dict_test = {'Key': 'DoNotDelete', 'Value': 'True'}
 
    my_region = os.environ['AWS_REGION']

    for snapID in oldAuroraSnapshots:
        ARN="arn:aws:rds:"+my_region+":"+m_account+":cluster-snapshot:"+snapID
        
        response = rds_client.list_tags_for_resource(ResourceName=ARN)
        
        if dict_test in response['TagList']:
            AurorasnapshotsWithTagTrue.append(snapID)
              
    auroraSnapshotsToDelete= [x for x in oldAuroraSnapshots  if x not in  AurorasnapshotsWithTagTrue]
        
    return auroraSnapshotsToDelete
    
def deleteAuroraSnapshots(auroraSnapshotsToDelete,rds_client):
    
    #---------------------------------------------
    # Deletes the Aurora snapshots which are manual
    #-----------------------------------------------
    for snap in auroraSnapshotsToDelete:
        try:
            response = rds_client.delete_db_cluster_snapshot(DBClusterSnapshotIdentifier=snap)
            logger.info("Deleted Aurora Snapshot having ID: " +snap  )
        except Exception as e:
            logger.info("Unable to delete the automated Aurora RDS Snapshot having ID: "+snap)
    
    logger.info("Done from function of Aurora Snapshots Deletion. ")            
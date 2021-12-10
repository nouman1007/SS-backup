# Log Monitoring with EK
   ControlTower provides cloudtrail(enabled for all the accounts out of the box) to collect accounts activity to Log account(S3 bucket as repo for logs data).

   This solution pick up logs data from S3 as source data and push it to ElasticSearch using Lambdas associated in this pacakge.
    
<img src="EK Design.jpg" alt="EK-Log Monitoring Solution Design" style="max-width:100%;">

## Components

- 3 Lambda functions and associated IAM Role & policies
    -   restart_sync
        -   Manually trigger if there is an error while getting events records from source bucket to sync_files
    -   setup_s3_events
        -   set events for source bucket where all the cloudtrail logs are stored
    -   sync_files
        -   this is the main Lambda function that get logs data from SQS as event and push it to ES with Index(date added with index name)
- ElasticSearch and access policy
    -   Deploy using CF with other components after packaging them and visulization all the logs activity using Kibana(ES manage service)
- SNS topic and subscription
    -   Trigger first email to subscriber when there is 1 event in deadletter queue
    -   Trigger second email to subscriber when there are 100 events in deadletter queue
- SQS for event error managment
    -   Handle events(log records) in case there is a failure in transmissiting events from source bucket to sync_files


## Deployment
   This solution deployed using cloudformation template "EK-Deploy.yaml" after pacakging it

Following components are deployed using this template:

   -  Set event on source bucket having log’s data. setup_s3_events.py is performing this function.
   -  Create ElasticSearch Domain.
   -  Push logs data from source bucket to ElasticSearch. sync_files.py is performing this function.
   -  Create main queue for processing the data from source s3 bucket and transfer to lambda function.
   -  Create deadletter queue to get the unprocessed data or which is not able to transfer to ElasticSearch for any reason.
   -  Manually trigger restart_sync lambda if there is an error while getting events records from source bucket to sync_files, it will          push message from deadletter queue to main queue.
   -  Create SNS topic for notifications.
   -  Deploys three lambda functions.

## Parameters in Template

|Parameter                |Description                                                            |Allowed values           |
|-------------------------|-----------------------------------------------------------------------|-------------------------|
|pAlertNotificationEmail  |Email where replication alerts will be sent                            |email only               |
|pDomainVersion           |Version for domain                                                     |7.4, 7.1, 6.8, 6.7, 6.5  |
|pFileSyncSourceBuckets   |Comma delimited list of bucket's arns for the sync_file source buckets |Must be arn              |
|pIndex                   |Index for ElasticSearch                                                |Small letters only       |
|pInstanceType            |Instance type for cluster                                              |r5.large.elasticsearch   |
|pMasterNodesCount        |Number of master nodes                                                 |Must be greater then 1   |
|pNodesCount              |Number of  nodes                                                       |At least 1               |



## Deployment steps

1. package template
   
      1.a aws cloudformation package --template-file EK-Deploy.yaml --s3-bucket <bucketname> --output-template-file <new-name>.yml
   
   For Example:
   
      1.b aws cloudformation package --template-file EK-Deploy.yaml --s3-bucket eq-skymap-log-cfdeploy --output-template-file EK-Deploy-packaged.yml
    

2. deploy template
    
    2.a via cli
        aws cloudformation deploy --template-file EK-Deploy-packaged.yml --stack-name <stackname> --capabilities CAPABILITY_IAM --parameter-overrides <parameter-name>=<value> --tags purpose=Log-monitoring-with-EK

    2.b
        Manually via aws cf console after using package output template file


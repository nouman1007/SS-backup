# Patch Management Using Systems Manager

The designed solution involves setting up the patch automation solution in each AWS account through AWS CloudFormation StackSets in a Master account, and configuring a resource data sync across the accounts with the Master account.  To extract value quickly from resource data sync(SSM Inventory), query the underlying data source using Amazon Athena.

## **AWS Services Used In Solution**

- AWS  resource data sync. 

- AWS S3 - to keep reports.

- AWS Glue Crawler - it runs periodically, scans the data and automatically populate the AWS Glue Data Catalog.

- AWS Glue Data Catalog - once data in Glue Data Catalog, it readily available to querying in Athena. 

- AWS Athena DataBase.

- AWS CloudFormation Template - to automate the solution.

- AWS QuickSight - to visualize the reports.

## Solution Design

![patch_solution-diagram](D:\Skysuit\AWS_Patch_Manager\Final\patch_solution-diagram.jpg)

## Deployment



1. In the master account, an AWS CloudFormation stack set is used to configure the S3 bucket for resource data sync through Systems Manager Inventory.

2. The CloudFormation stack set creates the stack with  the patch baselines, and sets up Systems Manager Inventory resource data sync on the application accounts, to synchronize resources in the shared services account.

3. The resource information in the application accounts is synchronized with the resource information in the shared services account.

4. Amazon QuickSight generates patch compliance reports, using the Amazon Athena dataset for the synchronized resource information.

   

| ***SrNo.\*** | ***File\***                                                 | ***Description\***                                           | ***Location\***                                           |
| ------------ | ----------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
|              | **Cloudformation  Template (Yaml)**                         |                                                              |                                                           |
| 1            | resourcedatasync_s3bucket_bucketpolicy.yml | Create S3 bucket, resourcedatasync and Put bucket policy. | eq-skybase\Patch Management\CloudFormation  Templates |
| 2            | windows_patch_baseline_maintenance_window.yml | Create patchbaseline, maintenancewindow & maintenancewindowtarget | eq-skybase\Patch Management\CloudFormation  Templates |
| 3            | resource_data_sync.yml | Create a resource data sync for systems manager to get inventory information. | eq-skybase\Patch Management\CloudFormation  Templates |
| 4            | Consolidated_billing_s3_glue_crawler_athena.yaml            | Create a crawler,  Database and Athena table. It will be able to get Inventory details  and put in athena table to be queried with other tables in  quicksight | eq-skybase\Patch Management\CloudFormation  Templates |
|              |                                                             |                                                              |                                                           |

​    

## **Deployment steps**

1. Steps for Collector Account
   - Sign Up AWS Quick Sight in Collector Account. That will be used for visualization of member accounts SSM Inventory reports(which include **Patch Summary**, **Compliance summary**, **etc**.).
   
   - Deploy **resourcedatasync_s3bucket_bucketpolicy.yml** . It will create  resources i.e  S3 bucket, resourcedatasync & bucket policy.

     **Parameters in Template**
   
     | Parameter                   | Description                                                  | Allowed values    |
     | --------------------------- | ------------------------------------------------------------ | ----------------- |
     | pResourceDataSyncBucketName | Name of resourcedataSync bucket in which  data will come from source accounts. | lower case        |
     | pDataSourceAccountID        | Source account id for bucket policy                          | 522955560990, etc |
     | pSyncName                   | Any name                                                     | Any name          |
     | pSyncType                   | SyncFromSource(from AWS Organizations or from multiple AWS Regions), SyncToDestination(data to an S3 bucket) | SyncToDestination |
     | pBucketRegion               | Bucket Region                                                | us-east-1, etc    |
     | pBucketPrefix               | Folder name inside bucket                                    | Any name          |
   
     
   
2. Steps for Source Account.
   - Deploy windows_patch_baseline_maintenance_window.yml. It will create PatchBaseline, MaintenanceWindow , MaintenanceWindowTarget & SNSTopic.

      **Parameters in Template**

      | Parameter                    | Description                                                  | Default / Allowed values |
      | ---------------------------- | ------------------------------------------------------------ | ------------------------ |
      |                              | **Patch Baseline Information**                               |                          |
      | pOrganization                | Organization name                                            | Enquizit                 |
      | pPatchBaselineName           | Name of Patch Baseline                                       | myPatchBaseline          |
      | pPatchGroups                 | Name of the patch group that should be registered with the patch baseline | Production               |
      | pApproveAfterDays            | The number of days after the release date of each patch matched by the rule that the patch is marked as approved in the patch baseline. | 7                        |
      |                              | **Approval Rules**                                           |                          |
      | pProduct                     | Select from list of product related to platform.             | WindowsServer2019        |
      | pClassification              | Select from list of classification related to update.        | CriticalUpdates          |
      | pSeverity                    | Select from list of severity.                                | Critical                 |
      | pComplianceLevel             | Select from list of compliance level.                        | CRITICAL                 |
      |                              | **Maintenance Window**                                       |                          |
      | pMaintenanceWindowName       | Name for Maintenance Window                                  | OSMaintenanceWindow      |
      | pAllowUnassociatedTargets    | Set AllowUnassociatedTargets value (boolean)                 | false                    |
      | pCutoff                      | The number of hours before the end of the maintenance window that Systems Manager stops scheduling new tasks for execution. | 1                        |
      | pDuration                    | The duration of the maintenance window in hours.             | 2                        |
      | pSchedule                    | The schedule of the maintenance window in the form of a cron. | cron(0 4 ? * * *)        |
      | pScheduleTimezone            | The time zone that the scheduled maintenance window executions are based on, in Internet Assigned Numbers Authority (IANA) format. | US/Eastern               |
      | pNotificationEmailAddress    | Email address for patching notification.                     | Email address            |
      |                              | **Maintenance Window Targets**                               |                          |
      | pMaintenanceWindowTargetName | name for the maintenance window target                       | SSMPatchManager          |
      | pTargetsKey                  | User-defined criteria for sending commands that target instances that meet the criteria. i.e. tag:ServerRole. | tag:Patch Group          |
      | pTargetsValue                | User-defined criteria that maps to Key. i.e. WebServer.      | Production               |
      | pOwnerInformation            | A user-provided value that will be included in any CloudWatch events that are raised while running tasks for these targets in this maintenance window. | SSM Patch manager        |
      |                              | **Maintenance Window Tasks**                                 |                          |
      | pMaxConcurrency              | The maximum number of targets this task can be run for, in parallel (From 1 to 7). | 1                        |
      | pMaxErrors                   | The maximum number of errors allowed before this task stops being scheduled (From 1 to 7). | 1                        |
      | pPriority                    | The priority of the task in the maintenance window. The lower the number, the higher the priority. Tasks that have the same priority are scheduled in parallel. | 0                        |
      | pTaskType                    | The type of task. Valid values are RUN_COMMAND, AUTOMATION, LAMBDA, STEP_FUNCTIONS. | RUN_COMMAND              |
      | pTaskArn                     | The resource that the task uses during execution.( a. For RUN_COMMAND and AUTOMATION task types, TaskArn is the SSM document name or Amazon Resource Name (ARN), b.For LAMBDA tasks, TaskArn is the function name or ARN. c.For STEP_FUNCTIONS tasks, TaskArn is the state machine ARN.) | AWS-RunPatchBaseline     |

      3. Steps for Source Account.

      - Deploy **resource_data_sync.yml** in collector account. It will configure SSM Inventory resourcedatasync with collector account s3 bucket.

        **Parameters in Template**

        | Parameter                   | Description                                                  | Default /  Allowed values |
        | --------------------------- | ------------------------------------------------------------ | ------------------------- |
        | pResourceDataSyncBucketName | Name of resourcedataSync bucket in which  data will come from source accounts. | lower case                |
        | pSyncName                   | Any name                                                     | Any name                  |
        | pSyncType                   | SyncFromSource(from AWS Organizations or from multiple AWS Regions), SyncToDestination(data to an S3 bucket) | SyncToDestination         |
        | pBucketRegion               | Bucket Region                                                | us-east-1, etc            |
        | pBucketPrefix               | Folder name inside bucket                                    | Any name                  |

        

        4. Steps for Collector Account.

        ​     Deploy consolidated_billing_s3_glue_crawler_athena.yaml will create following:

        - AWS Glue Crawler - to crawls on Bucket.
        - AWS Glue Database - crawler will populate it when ever there is new data in Bucket.
        - consolidated_billing_crawler_initializer.py - to initialize the crawler.
        - Athena Table - having data in table form.

        **Parameters in Template**

        | Parameter           | Description                                           | Default /  Allowed values                                    |
        | ------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
        | pCFNCrawlerName     | Name of crawler                                       | patching-crawler                                             |
        | pCFNDatabaseName    | Name of database                                      | patching-database                                            |
        | pCFNTablePrefixName | Name of prefix of tables                              | patching                                                     |
        | pBucketName         | Bucket name with folder name  <bucketname/foldername> | eq-resourcedatasync-us-east-1-112520250899/shared-account-522955560990 |

        
   ```
   
   ```

   ####  AWS cli packaged command:
       aws cloudformation package --template-file consolidated_billing_s3_glue_crawler_athena.yaml --s3-bucket ns-rep-lambda-code --output-template-file consolidated_billing_s3_glue_crawler_athena.yaml_packaged.yml

   


### **AWS QuickSight**

Once all data is ready in the tables of Athena, there’s need to execute the Custom SQL query in AWS QuickSight. In QuickSight perform following steps:

1. Go to Manage QuickSight.
2. Select **Security and Permissions** from left pane.
3. Choose **Add or Remove.**
4. Choose **Select S3 Buckets.**
5. Check Bucket A, Destination_Bucket and Bucket C.
6. Click on Finish and then Update.
7. Go to QuickSight Manage Data.
8. On the **Your Data Sets** page, choose **New data set**.
9. In the **FROM NEW DATA SOURCES** section of the **Create a Data Set** page, choose the **Athena** data source icon.
10. For **Data source name**, enter a descriptive name for the data source connection. 
11. On the **Choose your table** screen, choose **Use custom SQL**. Enter your query, or a placeholder query such as SELECT 1, and choose **Confirm SQL**.
12. Load data into memory with [SPICE](https://docs.aws.amazon.com/quicksight/latest/user/welcome.html#spice), choose **Import to SPICE for quicker analytics**. The green indicator shows whether you have space available.
13. To prepare the data before creating an analysis, choose **Edit/Preview data**. This opens the data preparation screen. When you are finished editing the dataset, choose **Save & Visualize** to go to analysis.
14. Perform following steps to create refresh schedule on dataset.
    1. On the **Your Data Sets** page, choose the dataset, and then choose **Schedule refresh**.
    2. For **Schedule Refresh**, choose **Create**.
    3. On the **Create a Schedule** screen, choose settings for your schedule.
       1. For **Time zone**, choose the time zone that applies to the data refresh.
       2. For **Repeats**, choose one of the following:
          - For Standard or Enterprise editions, you can choose **Daily**, **Weekly**, or **Monthly**.
            - **Daily**: Repeats every day
            - **Weekly**: Repeats on the same day of each week
            - **Monthly**: Repeats on the same day number of each month. To refresh data on the 29th, 30th or 31st day of the month, choose **Last day of month** from the list.
    4. **Starting**: Choose a date for the refresh to start.
    5. For **At**, Specify the time that the refresh should start. Use HH:MM and 24-hour format, for example 13:30.

## Deletion of Un attached Volumes, Old EBS Snapshots and Old RDS Snapshots.

---

### Description:
It is highly important to keep the track of cost occuring of each AWS Account. There are few resources that consumes the main part of budget which includes EC2 instances , Load Balancers , EIP , unattached vloumes, Snapshots etc.

Releasing the resources when free is highly important to in maintain the budget in control. The solution is capable to deleting the un attached volumes, RDS & EBS snapshots which are older than x number of days. 

### Pacakage Contents:

Package for solution contains:
1. CFT_vol_ebs_rds.yaml -  To deploy the lambda function and cloud watch event which triggers the lambda on specific time.

2. delete_vol_ebs_rds.zip - Actual functionality of deletion of resources based on some logic.

3. IAMtrustedRole.yaml - to create IAM Trusted role with name of "CrossAccountRole" in all member accounts. Lambda (which is in master account) will assume this role when comes to perform action in member account.

### Deployment Steps:

Solution is designed in such a way that single lambda function works for all accounts which are under master account, hence reducing the effort of same configuration for all accounts. 

Read the below steps carefully to deploy the solution in master account.

1. Solution assumes that all member accounts has IAM Trusted role with Master account. If Member accounts dosnot have IAM trusted role with Master account, then you need to deploy the **IAMtrustedRole.yaml** via StackSet from master account in all member accounts. 

2. Upload the **deletes_vol_ebs_rds.zip** provided in pacakege to s3 bucket in master account.

3. Go to Cloudformation Service and create Stack from there.

4. Choose the **CFT_vol_ebs_rds.yaml** template and provide the following parameters:

    a. NumberOfDays : Give any integer as number of days to filter out the snapshots.

    b. S3BucketName: Give the name of bucket in which zip file has been uploaded.

5. Create the Stack and wait for completion.

6. It will deploy the resources and Lambda function will start executing at specified time through Scheduled Cloudwatch Event. The specified time is 6:00AM Daily UTC. 

7. To change the time according to requirements, You have to modify it in CFT_vol_ebs_rds.yaml template.

### Current Status:

Solution is able to get the IDs of all member accocunts under master account and deletes the following:
1. Available/Unattched volumes.
2. Old EBS Snapshots which fall in following criteria:
    - Older than x number of days.
    - Having tag with key: DoNotDelete, Value:False
    - Do not have tag key: DoNotDelete
3. Old RDS Manual Snapshots which fall in following criteria:
    - Older than x number of days.
    - Having tag with key: DoNotDelete, Value:False
    - Do not have tag key: DoNotDelete
4. Old Aurora Manual Snapshots which fall in following criteria:
    - Older than x number of days.
    - Having tag with key: DoNotDelete, Value:False
    - Do not have tag key: DoNotDelete


---
### Note: Solution is not able to delete the Automated snapshots/System snapshots. 
---



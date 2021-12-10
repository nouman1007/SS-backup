**Set the retention period of cloudwatch logs from never expire  to certain limit(30days)**



**Deployment:**

Go to Master Account(Centralized account)

1- Deploy the cloud formation stack set in desired accounts (assume_role.yml) inside (Cloudwatch-Logs-Retention-Policy) folder.

*Output : we can get "name of assume Role" from output and which will be used as parameter in other cloudformation template.



Then




Go to the terminal i.e VSC(visual studio code)

1- Open the terminal.

2- Navigate into the cloudformation folder, where the yml file is present.

3- Put s3 bucket name in below CLI cloudformation packaged command (--s3-bucket <Bucket Name >).

4- Run the following aws CLI cloudformation packaged command:

 **aws cloudformation package --template-file cw_lgs_retention_policy.yml  --s3-bucket <Bucket Name >  --output-template-file cw_lgs_retention_policy_packaged_template.yml**



OutPut: in a result Will get a cloudformation packaged template.



Then



1-Deploy the cloudformation packaged template.



**Parameters**

| Parameter                      | Description                                 | Default                |
| ------------------------------ | ------------------------------------------- | ---------------------- |
| pAssumeRoleName                | To access from cross account                | CrossAccountAssumeRole |
| pCloudwatchLogsRetentionPeriod | Retention period of log group               | 30                     |
| pLambdaTiggerSchedular         | Time to trigger the lambda function         | cron(0 6 * * ? *)      |
| pOrganizationUnitId            | Organization unit ID inwhich accounts belog | ou-hlvo-4b0xc70g       |
| pTargetId                      | To Identify the Cloudwatch Rules            | cw-lg-expt-Func        |

​	
​	
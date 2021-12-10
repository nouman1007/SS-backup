
Go to Master Account(Centralized account)


1- Deploy the cloud formation stack set in desired accounts (assume_role.yml) inside (Cloudwatch-Logs-Retention-Policy) folder.

*Output : we can get "name of assume Role" from output and which will be used as parameter in other cloudformation template.




Then


Go to the terminal i.e VSC(visual studio code)

1- Open the terminal.

2- Navigate into the cloudformation folder, where the yml file is present.

3- Put s3 bucket name in CLI cloudformation packaged command (--s3-bucket <Bucket Name >).

4- Run the following aws CLI cloudformation packaged command:

 **aws cloudformation package --template-file cw_lgs_retention_policy.yml  --s3-bucket <Bucket Name >  --output-template-file cw_lgs_retention_policy_packaged_template.yml**


OutPut: in a result Will get a cloudformation packaged template.


Then


1-Deploy the cloudformation packaged template.



Parameters

Key			Value

pAssumeRoleName		CrossAccountAssumeRole	
pCloudwatchLogs		RetentionPeriod	30	
pLambdaTiggerSchedular	cron(0 6 * * ? *)	
pOrganizationUnitId	ou-hlvo-4b0xc70g	
pTargetId		cw-lg-expt-Function
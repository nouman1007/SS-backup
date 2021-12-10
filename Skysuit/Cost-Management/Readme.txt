
IN Master Account:

1- cloud formation template (Bucket-For-CFT-Multi-Acct.yml) inside (Cloudformation-for-lambda-bucket-4-multi-account) folder.

*This template will create s3 bucket to packaged the cloudformation template deployment in multiple accounts through stackset. 

2- After cloudformation successfully deploied, they get name of bucket from output section and put into below mentioned cloudformation packaged command.



Go to the terminal i.e VSC(visual studio code)

1- Open the terminal.

2- Navigate into the cloudformation folder, where the yml file is present.

3- Run the following cloudformation packaged command with Bucket name:

 **aws cloudformation package --template-file cw_lgs_retention_policy.yml  --s3-bucket <Bucket Name >  --output-template-file cw_lgs_retention_policy_packaged_template.yml**




IN Master Account:

1-Deploy the cloudformation packaged template through stackset in member accounts
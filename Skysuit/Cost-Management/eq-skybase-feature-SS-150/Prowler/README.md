Prowler creation to Monitor all member account in a organization using a Master Account
2021-06-11 


A. SUMMARY
==========
Prowler can be used to scan multiple account using AWS organization. Following steps can be followed to setup prowler for Multiple accounts. The following solution create a containerized prowler solution to scan the accounts in a organization and pushs the detected vulnerabilties to security Hub.The following solution enables the master account to monitor all member account in a organization using Prowler. 

Note: I assume that you have a ECR repository already available , you have the right permission already enabled in you account to use aws stacksets else you can deploy the AWSCloudFormationStackSetExecutionRole.yml (For member accounts) & ST-StacksetAdminRole.yaml (For master Account) CFT template 

B. PACKAGE CONTENTS
===================
a. CloudFormation Templates (cft/)
    i.     ProwlerS3.yaml
    ii.    Batch-job-prowler.yaml 
    iii.   ProwlerXA.yaml
    iv.    code-build.yaml
    v.     AWSCloudFormationStackSetExecutionRole.yml
    vi.    ST-StacksetAdminRole.yaml
b. ShellScripts
    i.      scripts.sh 
    ii.     execute.sh 
    iii.    run-prowler-reports.sh
    iv.     run-prowler-2.sh

c. Build Automation / CICD (buildautomation/)
    i.      buildspec.yml
    ii.     Dockerfile



C. DEPLOY MASTER ACCOUNT RESOURCES
==================================
1. Deploy ProwlerS3.yaml in the Logging Account. Specify the following paramters:
      AwsOrgId: organization id of master account that you want to monitor
      S3Prefix: prefix that will be used in the S3 bucket name.


2. Deploy ProwlerXA-Role.yaml. Specify the following paramters:

        a. ProwlerAccount:	Master account id	
        b. ProwlerCrossAccountRole: cross account Role
        c. ProwlerRole	ProwlerEC2-Role	 (Role for the EC2)
        d. ProwlerS3: Name of S3 bucket 

3. Deploy Codebuild.yaml. Specify the following paramters:
       a. ECRRepositoryURI	
       b. PersonalAccessToken: (you can get this from you github account)
       c. ROLE:  (Cross Account Role)
       d. S3Account: (Account of your S3 Bucket)	
       e. S3URI: (URI of your S3 Bucket)

4. Deploy Batch-job-prowler.yaml. Specify the following paramters:
       a. AwsOrgId	o-j00zam5ytf	
       b. CRON	cron(0 15 10 ? * *)	
       c. CrossAccountRole	ProwlerXA-Role	
       d. ECR	224233068863.dkr.ecr.us-east-1.amazonaws.com/prowler-image:latest	
       e. ProwlerS3	prowler-224233068863-us-east-1	
       f. VPC	vpc-c0e064bb	
       g. mySubnetIDs	subnet-8e4450ea



D. DEPLOY Member-ACCOUNT RESOURCES
===============================
1. This is done ideally using stacksets.

2. Deploy the ProwlerXA-Role.yaml CFT to the Member-accounts, ideally using stacksets.  Specify the following paramters:

            a. ProwlerAccount:	Master account id	
            b. ProwlerCrossAccountRole: cross account Role
            c. ProwlerRole	ProwlerEC2-Role	 (Role for the EC2)
            d. ProwlerS3: Name of S3 bucket 

Note: when you deploy the solution in a member account using stack sets you will have to ensure the following things

        a. Add account in trust relationship of Prowler-Xa role so that it can assume the ProwlerXA-Role i.e  "arn:aws:iam::224233068863:root"
        b. Make sure you Master Acc is a delegated Administrator of Security HUB
        c. Enable account as a member in Security Hub settings so the Master account so that security hub can monitor the account
        d. Make sure security hub in the member account is integrated with prowler to accept finding.



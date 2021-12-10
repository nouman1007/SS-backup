# Run Baseline Server Patching (Windows and Linux)

Dennis Christilaw edited this page on Oct 30, 2019 · [4 revisions](https://github.com/Talderon/AWS_CloudFormation/wiki/Run-Baseline-Server-Patching-(Windows-and-Linux)/_history)

# Purpose

This document will cover the creation of a Windows/Linux Server Patching Maintenance Windows, Task and Targets for the maintenance.

- ```
        Any items marked **(OPTIONAL)** can be removed if there is no need to specify this information
  ```

This Maintnance Window runs the following Document: AWS-RunPatchBaseline

This initiates running available Default Patch Baselines for Windows AND Linux Servers. For more information on baselines, refer to the following AWS Document:

[About Predefined and Custom Patch Baselines](https://docs.aws.amazon.com/en_pv/systems-manager/latest/userguide/sysman-patch-baselines.html)

# Targetting

If you only want to run this on specific OS's, you can accomplish this with intelligent tagging for the target machines. You do NOT need to include mixed OS version in just one maintenance window. It's better to break it up as various OS's and Distributions have varying patch cycles.

Microsoft releases patches on the Second Tuesday of every month (thus the friendly name of "Patch Tuesdays"). There are always exceptions for highly severe/critical patches, but those are always treated as one-off patches at any rate.

For a full list of Operating Systems/Distributions and Versions supported, visit this AWS Doc Page for details:

[Patch Manager Prerequisites](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager-prerequisites.html)

- Because of so many comments on this image - I stole this from AWS Published Documentation, this is **NOT** my account number. It's one that AWS uses as a sample, so I decided to "borrow" it as well.

# Prerequisites

Thew following work will need to be completed to be able to use this template:

- EC2 Instances need to be Tagged

- The Key :: Value pair needs to be unique for this process. The below is a suggestion that can be used or another set can be created for this work.

- Suggested Key is: Patch Group

- ```
        This key needs to be set EXACTLY as displayed above in order for Systems Manager to pick them up as a built in Patch Group.
  ```

- [About Patch Groups in AWS](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-patch-patchgroups.html)

- Suggested Value:

- ```
        This should be descriptive so users can understand which Patch Group servers belong too.
  ```

- Finding your account ID (Console)

![Console AccountId](https://github.com/Talderon/AWS_CloudFormation/raw/master/images/account-id-iam-console.png)

- Because of so many comments on this image - I stole this from AWS Published Documentation, this is **NOT** my account number. It's one that AWS uses as a sample, so I decided to "borrow" it as well.

- Finding your account ID (AWS CLi)

- ```
        aws sts get-caller-identity
  ```

- ARN of the SNS Topic to send notifications through (Optional, can be removed if no notification is needed)

- ```
        In order to get notifications (email, sms or other), you will need to create/use a topic, obtain the ARN and enter it here
  ```

- S3 Bucket Name to store logs / S3 Bucket prefix to assign logs for this job (Optional, can be removed if no log collection is needed)

- ```
        These need to already exist in order to be used
  ```

# Template Parameters

## Maintenance Window

- Maintenance Window Name (lowecase, no spaces)

- Maintenance Window Description (128 char max) **(OPTIONAL)**

- Timezone format as found here: [Time Zone Names](https://docs.aws.amazon.com/en_pv/redshift/latest/dg/time-zone-names.html)

- ```
        Use the labels on the linked page to ensure the job will run without issues in the timezone you select
        AWS will automatically convert this to UTC
  ```

- Maintenance Window Duration (in hours)

- Maintenance Window Cutoff (in hours before window closes) **(OPTIONAL)**

- ```
        New jobs will not be initiated on instances once this time is reached. Be sure to allow for enough time for the job to run on all instances!
  ```

- Maintenance Window Schedule

- ```
        Cron/Rate expression for schedule - Sample - cron(0 0 23 ? * WED *)
        This sample runs weekly, every Wed at 23:00 (11:00 pm)
  ```

- Documentation located here: [Schedule Expressions Using Rate or Cron](https://docs.aws.amazon.com/en_pv/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html)

## Maintenance Target Configuration

- Maintenance Target Config Name (lowercase, no spaces)

- Maintenance Target Config Description (128 char max) **(OPTIONAL)**

- Maintenance Target Tag Key (format: tag:{keyName})

- ```
        Value should look like: tag:AgentUpdate
  ```

- Maintenance Target Key Value

- ```
        For this template, the only value is True or False
        Case Sensitive
  ```

## Maintenance Run Command Configuration

- Run Command Name (lowercase, no spaces)

- Run Command Task Priority

- ```
        Values 0 - 5
        Default set to 1 - This does not need to be changed
  ```

- Run Command Max Concurrency **(OPTIONAL)**

- ```
        You can use an Integer or a Percent
  ```

- Run Command Max Error Rate **(OPTIONAL)**

- ```
        You can use an Integer or a Percent
  ```

- ARN of the SNS Topic to send notifications through **(OPTIONAL)**

- ```
        Must be a VALID ARN
  ```

- S3 Bucket Name to store logs **(OPTIONAL)**

- ```
        Bucket Name, NOT ARN
  ```

- S3 Bucket prefix to assign logs for this job **(OPTIONAL)**

The information provided in this Repo are licensed under the Apache 2.0 license. Please be respectful. Thanks!

###  Pages 12

- **[Home](https://github.com/Talderon/AWS_CloudFormation/wiki)**
- **[AWS ElassticSearch Service Troubleshooting and Resolution Guide](https://github.com/Talderon/AWS_CloudFormation/wiki/AWS-ElassticSearch-Service---Troubleshooting-and-Resolution-Guide)**
- **[AWS ElasticSearch Service Plus Cognito How To Put It All Together](https://github.com/Talderon/AWS_CloudFormation/wiki/AWS-ElasticSearch-Service-Plus-Cognito---How-To-Put-It-All-Together)**
- **[CloudFormation Template Notes (Kind of a Cheat Sheet?)](https://github.com/Talderon/AWS_CloudFormation/wiki/CloudFormation-Template-Notes-(Kind-of-a-Cheat-Sheet%3F))**
- **[Cognito Service CFN Tempalte](https://github.com/Talderon/AWS_CloudFormation/wiki/Cognito-Service-CFN-Tempalte)**
- **[DRAFT AWS Stored Parameters Use Cases](https://github.com/Talderon/AWS_CloudFormation/wiki/DRAFT---AWS-Stored-Parameters-Use-Cases)**
- **[ElasticSearch CloudFormation Tempaltes](https://github.com/Talderon/AWS_CloudFormation/wiki/ElasticSearch-CloudFormation-Tempaltes)**
- **[ElasticSearch Kibana API Documentation](https://github.com/Talderon/AWS_CloudFormation/wiki/ElasticSearch-Kibana-API-Documentation)**
- **[ElasticSearch Service Kibana Tips and Tricks](https://github.com/Talderon/AWS_CloudFormation/wiki/ElasticSearch-Service-Kibana-Tips-and-Tricks)**
- **[FunctionBeat Configuration "Gotcha's"](https://github.com/Talderon/AWS_CloudFormation/wiki/FunctionBeat-Configuration-"Gotcha's")**
- **[Run Baseline Server Patching (Windows and Linux)](https://github.com/Talderon/AWS_CloudFormation/wiki/Run-Baseline-Server-Patching-(Windows-and-Linux))**
- **[Run SSM Agent Update (Windows and Linux)](https://github.com/Talderon/AWS_CloudFormation/wiki/Run-SSM-Agent-Update-(Windows-and-Linux))**

##### Clone this wiki locally
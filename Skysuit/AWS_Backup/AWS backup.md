# Implement automated service level backup using AWS Backup



## Overview

Organizations want the ability to have a standardized way to manage their backups at scale. Administrators that previously had to manually duplicate backup configurations across thousands of accounts, can now manage and monitor backups through a single process, from a single master account. AWS backup service enables Organizations to standardize the way they implement backup policies, minimizing the risk for errors as well reducing the manual overhead.



AWS Backup serves as a single dashboard for backup, restore, and policy-based retention of different AWS resources, which include:

- Amazon EFS file systems

- DynamoDB tables

- Amazon EC2 instances (Does not support Amazon EC2 instance store-backed instances)

- Amazon EBS volumes

- Amazon RDS databases

  

 ![](D:\Skysuit\AWS_Backup\backup.png)



**Backup Vault**

A backup vault is a container to organize your backups in

- AWS Key Management Service (AWS KMS) encryption key that is used to encrypt backups in the backup vault and to control access to the backups in the backup vault.

**Backup Plans**

A backup plan is a policy expression that defines when and how you want to back up your AWS resources, such as Amazon DynamoDB tables or Amazon Elastic File System (Amazon EFS) file systems.

- Backup Rule

  Backup plans are composed of one or more backup rules.

  ​	Backup Rule Name (case sensitive, must contain from 1 to 63 alphanumeric characters or hyphens)

  ​	Backup Frequency  (frequency of every 12 hours, daily, weekly, or monthly)

  ​	Backup Window (begins and the duration of the window in hours)

  ​	Lifecycle (transitioned to cold storage and when it expires)

**Resource Assignments**

AWS Backup supports two ways to assign resources to a backup plan: by tag or by resource ID. Using tags is the recommended approach for several reasons:

- It’s an easy way to ensure that any new resources are automatically added to a backup plan, just by adding a tag.
- Because resource IDs are static, managing a backup plan can become burdensome, as resource IDs must be added or removed over time.

**Cross-Account Management**

-  Use backup policies to apply backup plans across the AWS accounts within your organization.
- Eliminate manually duplicating backup plans across individual accounts.

**Note:**

Before we can use the cross-account management feature, you must have an existing organization structure configured in AWS Organizations. 



#### **Parameters**



| Name                     | Description                                                  | Type     | Default            | Required |
| ------------------------ | ------------------------------------------------------------ | -------- | ------------------ | -------- |
| pBackupVaultName         | Name of backup vault (e.g. Prod)                             | `string` | Prodbackupvault    | yes      |
| pBackupPlanName          | Name of backup plan (e.g. Daily)                             | `string` | DailyBackupPlan    | yes      |
| pRuleName                | Rule name for backup plan                                    | `string` | WeeklyBackup       | yes      |
| pScheduleExpression      | A CRON expression specifying when AWS Backup initiates a backup job In UTC | `string` | cron(30 8 ? * * *) | yes      |
| pStartWindowMinutes      | The amount of time in minutes before beginning a backup. Minimum value is 60 minutes | `number` | 60                 | yes      |
| pCompletionWindowMinutes | The amount of time AWS Backup attempts a backup before canceling the job and returning an error. Must be at least 60 minutes greater than `start_window` | `number` | 120                | yes      |
| pBackupSelectionName     | Backup Resource Selection name                               | `string` | prod               | yes      |
| pResourcesTagKey         | The Tag Key of resources which is going to be backup         | `string` | environment        | yes      |
| pResourcesTagValue       | The Tag value of resources which is going to be backup       | `string` | prod               | yes      |
| pRetentionPeriod         | Specifies the number of days after creation that a recovery point is deleted. Must be 90 days greater than `cold_storage_after` | `number` | 365                | yes      |
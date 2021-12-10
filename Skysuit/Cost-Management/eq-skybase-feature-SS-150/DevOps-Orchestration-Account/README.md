# DevOps Orchestration Master Account
2021-03-16 Enquizit.inc

DevOps Master Account in Landing zone orchestrate the deployments of resources from single account. Only DevOps users can have access to master account. Instead of deploying same infrasturcture multiple times at different accounts, they can now deploy & manage it from DevOps master account.

In order to meet the requirements of multi account and multi region deployment, StackSet is important feature in AWS CloudFormation. The process includes definition of an AWS resource configuration in a CloudFormation template and then roll it out across multiple AWS accounts and/or Regions with a couple of clicks. The administrator account owns one or more StackSets and controls deployment to one or more target accounts. The administrator account must include an assumable IAM role and the target accounts must delegate trust to the administrator account

<img src="Design.png" alt="Master and Target account stack-set deployment design" style="max-width:100%;">

## Components:
a. AdminRole.yaml

b. ExecutionRole.yaml

## Parameters in Template:

|Parameter       |Description                                                                           |Allowed values |
|----------------|--------------------------------------------------------------------------------------|---------------|
|MasterAccountId |AWS Account Id of the master account (the account in which StackSets will be created).| Valid AWS Account Id      |

## Deployment steps:

Follow the mentioned steps to orchestrate the Master account using StackSet:

1) Deploy AdministrationRole.yaml  into Master Account. This creates a cross-account role called AWSCloudFormationStackSetAdministrationRole that CloudFormation will use to assume the AWSCloudFormationStackSetExecutionRole in each of the Target Accounts

2) Deploy ExecutionRole.yaml  into each of Target Account. This creates the AWSCloudFormationStackSetExecutionRole that the CloudFormation service will assume to deploy StackSets in the Target Accounts

3) Select the CloudFormation template(s) in master account you would like to deploy into the Target Accounts

a) Give meaningful name to StackSet

b) Specify stack parameters as you would a single CloudFormation template. These parameters will be applied in each Target Account

c) Enter appropriate tags to identify rescources

d) Select one of the permissions

    - Service Manged Permissions - allows StackSets to automatically configure the necessary IAM permissions required to deploy stack to the accounts in your organization

    - Self managed permissions - Choose the IAM role AWSCloudFormationStackSetAdministrationRole for CloudFormation to use for all operations performed on the stack 

e) Select one of the deployment options

    - Account Numbers - Specify the account numbers of the Target Accounts

    - Organization unit - Specify the OU ID

f) Specify the region(s)

g) Determine deployment strategy (like multiple regions, multiple accounts etc)

h) Review the deployment

i) Create StackSet

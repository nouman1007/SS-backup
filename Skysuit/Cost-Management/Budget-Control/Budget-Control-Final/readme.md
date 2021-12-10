# Use AWS Budgets alerts in the member accounts to move the AWS account to an OU with restrictive SCPs



- **Quarantine the account to an organization unit in** [**AWS Organizations**](https://aws.amazon.com/organizations/) **with restrictive SCPs.** This approach enables to apply specific restrictions per account basis. However, you’ll have to predefine an OU where the account should be moved after a budget condition breach.
- The budget is set by the owners of member accounts and not the management account. In this scenario, the owners of the member account manage their own cloud spend for their individual accounts. After the budget threshold for the member account is met, the management account moves the member account to another restrictive OU. 

### SCP

The restrictive policies on this new OU can be adjusted according to your needs. 

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:Create*",
        "ec2:Create*",
        "cloudtrail:Create*",
        "elasticsearch:Create*",
        "iam:Create*",
        "elasticloadbalancingv2:Create*",
        "acm:Create*",
        "rds:Create*",
        "redshift:Create*",
        "ssm:Create*",
        "cloudwatch:Create*",
        "cloudformation:Create*",
        "autoscaling:Create*",
        "dynamodb:Create*",
        "codebuild:Create*",
        "waf:Create*",
        "cloudfront:Create*",
        "lambda:Create*",
        "networkfirewall:Create*",
        "elasticbeanstalk:Create*",
        "wafv2:Create*",
        "shield:Create*",
        "shieldregional:Create*",
        "wafregional:Create*",
        "apigateway:Create*",
        "apigatewayv2:Create*",
        "config:Create*",
        "codepipeline:Create*",
        "servicecatalog:Create*",
        "sqs:Create*",
        "kms:Create*",
        "qldb:Create*",
        "secretsmanager:Create*",
        "sns:Create*"
      ],
      "Resource": "*",
      "Effect": "Deny"
    }
  ]
}
```



### Prerequisites

- [Enable trusted access with AWS Organizations](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-enable-trusted-access.html?icmpid=docs_cfn_console) to use service managed permissions.
- [Create an OU](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous.html#create_ou) with restrictive SCPs. The member accounts will be moved to this OU when the budget is breached.
- You must have already set budgets for the member accounts.

Solution Diagram



![The workflow in the diagram is described in the body of the post.](https://d2908q01vomqb2.cloudfront.net/972a67c48192728a34979d9a35164c1295401b71/2021/05/03/Picture2_5.png)





The workflow  includes the following steps:

1. The owner of the member account sets the budget and threshold for the account.
2. When the budget threshold is reached, an SNS notification is sent.
3. The SNS notification triggers a Lambda function.
4. The Lambda function parses the budget breach notification and places that event on the management account’s event bus.
5. The management account’s event bus triggers the [Amazon CloudWatch Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html) rule.
6. The rule invokes a Lambda function.
7. The Lambda function moves the member account to an OU with more restrictive policies. In this case, the SCP on this new OU is shown in the preceding example.
8. The Lambda function sends an email to notify recipients of this move.



### Deployment Steps:

Note: Need a bucket with Bucket policy to deploy in cross account 

Go to the terminal i.e VSC(visual studio code)

1- Open the terminal.

2- Navigate into the cloudformation folder, where the yml file is present.

3- Run the following cloudformation packaged command with Bucket name:

 **aws cloudformation package --template-file budget_control.yml  --s3-bucket <Bucket Name >  --output-template-file budget_control_packaged_template.yml**

​																**&**

 **aws cloudformation package --template-file budget_control_member_acct.yml  --s3-bucket <Bucket Name >  --output-template-file budget_control_member_acct_packaged_template.yml**





- After run the AWS cli packaged command,  Choose the  budget_control_packaged_template.yml template from cloud formation folder and deploy in master account through cloud formation stack.
- Enter a unique name for the stack (for example, `budget-control-stack-member-accounts`).

**In Parameters**

- For **AccountList**, enter a comma-separated list of member account numbers for cross account permission. Enclose the account numbers in quotation marks (“).
- For **QuarantineOU,** enter the ID of the OU where you want to move the account to.

- In **Capabilities and transforms**, select the checkboxes to acknowledge that AWS CloudFormation will create IAM resources, AWS CloudFormation might create IAM resources with custom names, and AWS CloudFormation might require the following capability: `CAPABILITY_AUTO_EXPAND`.
- Choose **Create stack**.





**After the stack deployment:** 

- Choose the  budget_control_member_acct_packaged_template.yml  template   from cloudformation folder and deploy in master account through cloud formation stackset.

- In **Set deployment options**, choose **Deploy to organizational units (OUs)**. The members account.
- Under **Specify regions**, choose an AWS Region, and then choose **Next**.
- On parameter values**, enter the account ID of the management account, and then choose **.
- After the stack sets are successfully deployed, update the budgets of the member accounts with the SNS topic ARN you got from output.



Note :

- ​      After you have determined the reason for the cost increase, you can manually move back the member account back to its original OU.



## Conclusion

After the budget threshold is breached for one of the member accounts entered in the **AccountList** parameter, this solution will move that member account to the restrictive OU specified in the **QuarantineOU** parameter. You’ll also get an email notifying you on 80% of budget threshold & of this move upon 100% threshold.


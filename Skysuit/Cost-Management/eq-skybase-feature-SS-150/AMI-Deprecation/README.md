## AMI Depreciation Process for non complaint AMIs.

Solution is able to find the ec2 instances which are using non-compliant/deprecated AMI's and auto-remediate them.

2021-02-03 v1.0

======================================== 

## Package Contents
a. Deprecated_AMIs.yaml 

b. readme.md (this file)

c. custom_config_rule_function.py



## Configuration
1. Solution works for Custom AMIs. As, AMIs created via EC2 Image builder pipeline are tagged automatically with Key = Deprecation-Date and Value = 6 months from creation date. 

2. Enable the AWS Config in working region if not!  

3. Zip the **custom_config_rule_function.py** file and upload it to s3 bucket.

## Deployment of Deprecated_AMIs.yaml

1. Log into the Account.

2. Select CloudFormation.

3. Select 'Create Stack'.

4. Select 'Template is Ready', 'Upload a template file' and then 'Choose file'. Select the file **Deprecated_AMIs.yaml** which is included with this package.

5. Click 'Next'.

6. Enter a name for the Stack e.g. deprecated-ami-stack.

7. Enter the following parameters: 

    |Parameters|Description|Allowed Values|
    -----------|------------|---------------|
    |pCustomConfigRuleFunction|Specify name for custom config rule lambda function|sample-function|
    |pSNSTopic|SNS topic name for notifications|sample-topic|
    |pSNSEmailAddress|The endpoint that receives notifications from the Amazon SNS topic|******@enquizit.com|
    |pConfigRuleName|The name that you assign to the AWS Config rule.|deprecated-amis-by-tag|
    |pCloudWatchConfigEvent|Cloud Watch event rule name for Config Rule Compliance Change|sample-cwe|
    |pS3bucket|Specify bucket of python script|test-bucket|
    |pS3Key|Specify zip file name of python script|code.zip|
    ----------------------------------------------------------------------------------

8. Click 'Next'.

9. Check the box "I acknowledge that AWS CloudFormation might create IAM resources."

10. Click 'Submit'.

### Output: 

This template creates a Config rule, CloudWatch event and an AWS SNS topic. You can find the names in the output section of the CloudFormation stack.

### Result:

All running instances that are using deprecated AMIs means AMIs which are 6 months old from current date, will automatically stop and notification will be received at mentioned endpoint. Any changes in resource type will triggers the Config rule which in turn triggers the lambda function which will evaluate the complaince of resource and shows it at Config Rule Console.


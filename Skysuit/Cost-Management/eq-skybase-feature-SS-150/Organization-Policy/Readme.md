# AWS Orgnization Unit Service Control policy implementation
2020-04-07
Enquizit.inc

## Package Contents

a. ctpolicycreator.py

b. deployment.yml

c. ctpolicycreator.zip

## Deployment steps

1. package template
   
      aws cloudformation package --template-file deployment.yml --s3-bucket <bucketname> --output-template-file <new-name>.yml
   
   For Example:
   
      
      aws cloudformation package --template-file deployment.yml --s3-bucket eq-skybase-cfdeploy --output-template-file deployment-packaged.yml
    

2. deploy template
    
    2.a via cli

        aws cloudformation deploy --template-file deployment-packaged.yml --stack-name <stackname> --capabilities CAPABILITY_IAM

        e.g, 

        aws cloudformation deploy --template-file deployment-packaged.yml --stack-name eq-orgpolicies --capabilities CAPABILITY_IAM

    2.b

        Manually via aws cf console after using package output template file
 
3. Run the cloudformation template and it will create all the manadatory polices
4. PolicyType can either be "TAG_POLICY" or "SERVICE_CONTROL_POLICY"
5. To update the policy, update the cloudformation template file `deployment.yml` and and execute changeset to update existing policies

e.g

```
rCustomSCP:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      ServiceToken: !GetAtt PolicyCreatorFn.Arn
      PolicyName: !Sub ${AWS::StackName}-SCP
      PolicyType: SERVICE_CONTROL_POLICY
      Description: "This SCP denies access to any operations outside of the specified AWS
      Region, except for actions in the listed services (These are global
      services that cannot be whitelisted based on region)"
      PolicyDoc:
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "NotAction" : [
                      "iam:*",
                      "organizations:*",
                      "route53:*",
                      "budgets:*",
                      "waf:*",
                      "cloudfront:*",
                      "globalaccelerator:*",
                      "importexport:*",
                      "support:*",
                      "health:*",
                      "route53domains:*"
                    ],
                    "Effect": "Deny",
                    "Resource": "*",
                    "Condition": {
                        "StringNotEquals": {
                            "aws:RequestedRegion": [
                                "us-east-1",
                                "us-west-1"
                            ]
                        }
                    }
                }
            ]
        }


rTagPolicyEQTagPolicy:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      ServiceToken: !GetAtt PolicyCreatorFn.Arn
      PolicyName: !Sub ${AWS::StackName}-EQTags
      PolicyType: TAG_POLICY
      Description: "This policy enforce tagging to all the ec2 instances."
      PolicyDoc:
          {
              "tags": {
                  "eq-schedule": {
                      "tag_value": {
                          "@@assign": [
                              "eq-default-8pm-est-stop"
                          ]
                      },
                      "enforced_for": {
                          "@@assign": [
                              "ec2:instance"
                          ]
                      }
                  }
              }
          }

7. To delete the policy, delete the cloudformation template and it will delete all the polices

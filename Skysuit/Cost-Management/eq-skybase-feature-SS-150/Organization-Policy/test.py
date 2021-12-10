import os
# import datetime
from datetime import date, timedelta, datetime
import ctpolicycreator



os.environ['AWS_PARTITION'] = "aws"  #(datetime.strptime(datetime.today().strftime('%m%d%y'),'%m%d%y')) - timedelta(days = 1)
os.environ['logging_level'] = "INFO" #ab-test-activity-logging"
os.environ['regions_list'] = "us-east-1" #ab-test-activity-logging"


# policydoc =       {
#         "PolicyName": "Retention",
#         "Description":"The name of the application being run on the instance.",
#         "content": {
#             "tags": {
#                 "Retention": {
#                     "enforced_for": {
#                         "@@assign": [
#                             "ec2:instance",
#                             "ec2:volume",
#                             "redshift:*",
#                             "s3:bucket"
#                         ]
#                     }
#                 }
#             }
#         }
# }

policydoc =      {
            "tags": {
                "Retention": {
                    "enforced_for": {
                        "@@assign": [
                            "ec2:instance",
                            "ec2:volume",
                            "redshift:*",
                            "s3:bucket"
                        ]
                    }
                }
            }
        }
      

samplecreateevent = {
    "RequestType": "Create",
    "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:Sttest9-PolicyCreatorFn-1O6ERJZ69T22K",
    "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A224233068863%3Astack/Sttest9/bd60ba70-37b6-11ea-a7cb-0e3b177c99d5%7CrTagPolicyCustomerNumber%7Ce5da4114-bb37-49a7-a3c3-2ca5272fc52c?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200115T164814Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTTDO5TXT2%2F20200115%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=2f3a9501dc966563d58a76a0f58c98bfe33a3930a76fc5bf386f7631271e8dbf",
    "StackId": "arn:aws:cloudformation:us-east-1:224233068863:stack/Sttest9/bd60ba70-37b6-11ea-a7cb-0e3b177c99d5",
    "RequestId": "e5da4114-bb37-49a7-a3c3-2ca5272fc52c",
    "LogicalResourceId": "rTagPolicyCustomerNumber",
    "ResourceType": "AWS::CloudFormation::CustomResource",
    "ResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:Sttest9-PolicyCreatorFn-1O6ERJZ69T22K",
        "PolicyType": "TAG_POLICY",
        "Description": "A unique customer # assigned to this customer by UFIT.-1",
        "PolicyName": "Sttest9-CustomerNumber-2",
        "PolicyDoc": {
            "tags": {
                "Customer Number": {
                    "enforced_for": {
                        "@@assign": [
                            "ec2:instance"    
                        ]
                    }
                }
            }
        }
    }
}

sampleinvalid= {
    "RequestType": "Invalid",
    "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:Sttest9-PolicyCreatorFn-1O6ERJZ69T22K",
    "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A224233068863%3Astack/Sttest9/bd60ba70-37b6-11ea-a7cb-0e3b177c99d5%7CrTagPolicyCustomerNumber%7C895ac40a-bc53-42a5-a2e8-b5040fb5b41d?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200115T165331Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTTDO5TXT2%2F20200115%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=4be517bd6994222eb103985d5216a8fc2d5c83cb47f356b2e28913b257599b73",
    "StackId": "arn:aws:cloudformation:us-east-1:224233068863:stack/Sttest9/bd60ba70-37b6-11ea-a7cb-0e3b177c99d5",
    "RequestId": "895ac40a-bc53-42a5-a2e8-b5040fb5b41d",
    "LogicalResourceId": "rTagPolicyCustomerNumber",
    "PhysicalResourceId": "arn:aws:organizations::224233068863:policy/o-j00zam5ytf/tag_policy/p-95qplkz1rw",
    "ResourceType": "AWS::CloudFormation::CustomResource",
    "ResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:Sttest9-PolicyCreatorFn-1O6ERJZ69T22K",
        "PolicyType": "TAG_POLICY",
        "Description": "A unique customer # assigned to this customer by UFIT.-2",
        "PolicyName": "Sttest9-CustomerNumber",
        "PolicyDoc": {
            "tags": {
                "Customer Number": {
                    "enforced_for": {
                        "@@assign": [
                            "ec2:instance"
                        ]
                    }
                }
            }
        }
    }
}

sampledeleteevent= {
    "RequestType": "Delete",
    "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:Sttest9-PolicyCreatorFn-1O6ERJZ69T22K",
    "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A224233068863%3Astack/Sttest9/bd60ba70-37b6-11ea-a7cb-0e3b177c99d5%7CrTagPolicyCustomerNumber%7C895ac40a-bc53-42a5-a2e8-b5040fb5b41d?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200115T165331Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTTDO5TXT2%2F20200115%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=4be517bd6994222eb103985d5216a8fc2d5c83cb47f356b2e28913b257599b73",
    "StackId": "arn:aws:cloudformation:us-east-1:224233068863:stack/Sttest9/bd60ba70-37b6-11ea-a7cb-0e3b177c99d5",
    "RequestId": "895ac40a-bc53-42a5-a2e8-b5040fb5b41d",
    "LogicalResourceId": "rTagPolicyCustomerNumber",
    "PhysicalResourceId": "arn:aws:organizations::224233068863:policy/o-j00zam5ytf/tag_policy/p-95ndp015y1",
    "ResourceType": "AWS::CloudFormation::CustomResource",
    "ResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:Sttest9-PolicyCreatorFn-1O6ERJZ69T22K",
        "PolicyType": "TAG_POLICY",
        "Description": "A unique customer # assigned to this customer by UFIT.-2",
        "PolicyName": "Sttest9-CustomerNumber",
        "PolicyDoc": {
            "tags": {
                "Customer Number": {
                    "enforced_for": {
                        "@@assign": [
                            "ec2:instance"
                        ]
                    }
                }
            }
        }
    }
}

sampleupdateevent = {
    "RequestType": "Update",
    "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:ST-tagtest-PolicyCreatorFn-VCSNKBY86ROX",
    "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A224233068863%3Astack/ST-tagtest/2ab03f10-3889-11ea-86be-0e715b49d7c1%7CrTagPolicyUFIT%7C1ff7d2bc-c6c4-44a8-9ea2-a19bf033e7aa?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200116T175700Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTTDO5TXT2%2F20200116%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=8b82315ad77df05e247120e73228d8ae704c7638bd801a4c8ceddc8682247c24",
    "StackId": "arn:aws:cloudformation:us-east-1:224233068863:stack/ST-tagtest/2ab03f10-3889-11ea-86be-0e715b49d7c1",
    "RequestId": "1ff7d2bc-c6c4-44a8-9ea2-a19bf033e7aa",
    "LogicalResourceId": "rTagPolicyUFIT",
    "PhysicalResourceId": "arn:aws:organizations::224233068863:policy/o-j00zam5ytf/tag_policy/p-95ndp015y1",
    "ResourceType": "AWS::CloudFormation::CustomResource",
    "ResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:ST-tagtest-PolicyCreatorFn-VCSNKBY86ROX",
        "PolicyType": "TAG_POLICY",
        "Description": "The name of the application being run on the instance.-2",
        "PolicyName": "ST-tagtest-UFIT-updated",
        "PolicyDoc": {
            "tags": {
                "UFIT": {
                    "tag_value": {
                        "@@assign": [
                            "True",
                            "False"
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
    },
    "OldResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-east-1:224233068863:function:ST-tagtest-PolicyCreatorFn-VCSNKBY86ROX",
        "PolicyType": "TAG_POLICY",
        "Description": "The name of the application being run on the instance.-2",
        "PolicyName": "ST-tagtest-UFIT",
        "PolicyDoc": {
            "tags": {
                "UFIT": {
                    "tag_value": {
                        "@@assign": [
                            "True",
                            "False"
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
    }
}


# print(event)

class context:
    aws_request_id = 'aaa89780780b8yu080j0mjh0'
    invoked_function_arn = "arn:aws:lambda:us-east-1:834800198471:function:St-GuardDuty"
    log_stream_name = "log stream"
context = context()
response =ctpolicycreator.lambda_handler(sampledeleteevent, context)
# print(response) 






    



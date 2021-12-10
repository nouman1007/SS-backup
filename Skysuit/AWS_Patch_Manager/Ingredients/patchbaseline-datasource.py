# ==============Create Ptach Baseline===================================================

response = client.create_patch_baseline(
    OperatingSystem='WINDOWS'|'AMAZON_LINUX'|'AMAZON_LINUX_2'|'UBUNTU'|'REDHAT_ENTERPRISE_LINUX'|'SUSE'|'CENTOS'|'ORACLE_LINUX'|'DEBIAN',
    Name='string',
    GlobalFilters={
        'PatchFilters': [
            {
                'Key': 'PATCH_SET'|'PRODUCT'|'PRODUCT_FAMILY'|'CLASSIFICATION'|'MSRC_SEVERITY'|'PATCH_ID'|'SECTION'|'PRIORITY'|'SEVERITY',
                'Values': [
                    'string',
                ]
            },
        ]
    },
    ApprovalRules={
        'PatchRules': [
            {
                'PatchFilterGroup': {
                    'PatchFilters': [
                        {
                            'Key': 'PATCH_SET'|'PRODUCT'|'PRODUCT_FAMILY'|'CLASSIFICATION'|'MSRC_SEVERITY'|'PATCH_ID'|'SECTION'|'PRIORITY'|'SEVERITY',
                            'Values': [
                                'string',
                            ],
                            'Key': 'PATCH_SET'|'PRODUCT'|'PRODUCT_FAMILY'|'CLASSIFICATION'|'MSRC_SEVERITY'|'PATCH_ID'|'SECTION'|'PRIORITY'|'SEVERITY',
                            'Values': [
                                'string',
                            ]

                        },
                    ]
                },
                'ComplianceLevel': 'CRITICAL'|'HIGH'|'MEDIUM'|'LOW'|'INFORMATIONAL'|'UNSPECIFIED',
                'ApproveAfterDays': 123,
                'ApproveUntilDate': 'string',
                'EnableNonSecurity': True|False
            },
        ]
    },
    ApprovedPatches=[
        'string',
    ],
    ApprovedPatchesComplianceLevel='CRITICAL'|'HIGH'|'MEDIUM'|'LOW'|'INFORMATIONAL'|'UNSPECIFIED',
    ApprovedPatchesEnableNonSecurity=True|False,
    RejectedPatches=[
        'string',
    ],
    RejectedPatchesAction='ALLOW_AS_DEPENDENCY'|'BLOCK',
    Description='string',
    Sources=[
        {
            'Name': 'string',
            'Products': [
                'string',
            ],
            'Configuration': 'string'
        },
    ],
    ClientToken='string',
    Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ]
)

# ================================register_patch_baseline_for_patch_group=============================

response = client.register_patch_baseline_for_patch_group(
    BaselineId='string',
    PatchGroup='string'
)

# ==============================Delete Patch Baseline===============================================

response = client.delete_patch_baseline(
    BaselineId='string'
)

# ===============================Create data sync=====================================================

response = client.create_resource_data_sync(
    SyncName='string',
    S3Destination={
        'BucketName': 'string',
        'Prefix': 'string',
        'SyncFormat': 'JsonSerDe',
        'Region': 'string',
        'AWSKMSKeyARN': 'string',
        'DestinationDataSharing': {
            'DestinationDataSharingType': 'string'
        }
    },
    SyncType='string',
    SyncSource={
        'SourceType': 'string',
        'AwsOrganizationsSource': {
            'OrganizationSourceType': 'string',
            'OrganizationalUnits': [
                {
                    'OrganizationalUnitId': 'string'
                },
            ]
        },
        'SourceRegions': [
            'string',
        ],
        'IncludeFutureRegions': True|False
    }
)

# ==========================Delete data SyncSource========================================================

response = client.delete_resource_data_sync(
    SyncName='string',
    SyncType='string'
)

# ==================deregister_patch_baseline_for_patch_group==============================================

response = client.deregister_patch_baseline_for_patch_group(
    BaselineId='string',
    PatchGroup='string'
)

# =============================register_task_with_maintenance_window========================================

response = client.register_task_with_maintenance_window(
    WindowId='string',
    Targets=[
        {
            'Key': 'string',
            'Values': [
                'string',
            ]
        },
    ],
    TaskArn='string',
    ServiceRoleArn='string',
    TaskType='RUN_COMMAND'|'AUTOMATION'|'STEP_FUNCTIONS'|'LAMBDA',
    TaskParameters={
        'string': {
            'Values': [
                'string',
            ]
        }
    },
    TaskInvocationParameters={
        'RunCommand': {
            'Comment': 'string',
            'CloudWatchOutputConfig': {
                'CloudWatchLogGroupName': 'string',
                'CloudWatchOutputEnabled': True|False
            },
            'DocumentHash': 'string',
            'DocumentHashType': 'Sha256'|'Sha1',
            'DocumentVersion': 'string',
            'NotificationConfig': {
                'NotificationArn': 'string',
                'NotificationEvents': [
                    'All'|'InProgress'|'Success'|'TimedOut'|'Cancelled'|'Failed',
                ],
                'NotificationType': 'Command'|'Invocation'
            },
            'OutputS3BucketName': 'string',
            'OutputS3KeyPrefix': 'string',
            'Parameters': {
                'string': [
                    'string',
                ]
            },
            'ServiceRoleArn': 'string',
            'TimeoutSeconds': 123
        },
        'Automation': {
            'DocumentVersion': 'string',
            'Parameters': {
                'string': [
                    'string',
                ]
            }
        },
        'StepFunctions': {
            'Input': 'string',
            'Name': 'string'
        },
        'Lambda': {
            'ClientContext': 'string',
            'Qualifier': 'string',
            'Payload': b'bytes'
        }
    },
    Priority=123,
    MaxConcurrency='string',
    MaxErrors='string',
    LoggingInfo={
        'S3BucketName': 'string',
        'S3KeyPrefix': 'string',
        'S3Region': 'string'
    },
    Name='string',
    Description='string',
    ClientToken='string'
)


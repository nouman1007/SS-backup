import os
import json
from sync_files import sync_files



s3testevent = {
    "Records": [
        {
            "messageId": "ba1cff6b-a1bf-46e9-b0d8-2826218b0766",
            "receiptHandle": "AQEBm3RNSD04tsecuLqiqMtQsyrgXZxmtjuKHs1e684cARSkY2qNi9ZNPC7PFrrCFzCiS/8w3KpV1PuRWmoA9SvcyrOzVheq7te2AOMuOgNvJ4/WJMUohQRH877RJhmK2Fb518nYVkgZCRhxObM/hmm7FNXf8Cl6RgzW5Uhxx+Su80XZY+7AbdTVeqriSYR/kbLS/HSPy2qVuVoxrFNG7bdKXnkZKorjxsKk6YNddYJorevJT7KdnoG8WfIYKe4PxeF0x+1DUrL8kvCkn2nf8ww/qWMPTOK4hLEuem7+5Xy+LAHhvXlkXil7TE4X0bHc0EYh6yzKApN+gMdTHrDF8p8wUCuoYWvWDv62NkwhXhn7EW1tevK8zISrzTohOh2uFNdyBXrt4MWhmVtCeyn9VlsDqT4+gwA6PXBgsFXN9zDV5Jr5m6SeqfSinyvbGpJVbUfj",
            "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2020-04-16T17:14:58.869Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAJDIZMEIAORSYBIT7U\"},\"requestParameters\":{\"sourceIPAddress\":\"10.247.253.170\"},\"responseElements\":{\"x-amz-request-id\":\"678A33C9B769EE9E\",\"x-amz-id-2\":\"lQxws+9cupE0vyCnQR7JiuW2YYL9rVONgzmKxNLvlff+AyOVqOh1Oh68V0QVIj35ouW0x7NV4CvbFyF1fgLnS9LNLbQ6ssRl\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"S3_Put_Events_To_SQS\",\"bucket\":{\"name\":\"aws-controltower-logs-376773251456-us-east-1\",\"ownerIdentity\":{\"principalId\":\"A325ACLLLUO7QC\"},\"arn\":\"arn:aws:s3:::aws-controltower-logs-376773251456-us-east-1\"},\"object\":{\"key\":\"o-srsgnvvcqo/AWSLogs/627240122275/Config/ConfigWritabilityCheckFile\",\"size\":0,\"eTag\":\"d41d8cd98f00b204e9800998ecf8427e\",\"versionId\":\"VbhYoFa.jus9TZtiIQlIITSFi9zxjaKp\",\"sequencer\":\"005E98929764B355EB\"}}}]}",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1587057304683",
                "SenderId": "AIDAJHIPRHEMV73VRJEBU",
                "ApproximateFirstReceiveTimestamp": "1587057304684"
            },
            "messageAttributes": {},
            "md5OfBody": "9d4131a4f279872763e50cf88897cf93",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-1:376773251456:eq-LogMonitorin-Test-rMainSqsQueue-FIH00C36P1DL",
            "awsRegion": "us-east-1"
        }
    ]
}



class context:
    requestid=1111
    invoked_function_arn = "arn:aws:lambda:us-east-1:834800198471:function:ST-s3syncv9-rSyncFilesLambda-V0U93NH5PY1X"


Context = context()



os.environ["ES_HOST"] = "	search-eq-logm-relast-1ig7gb3gvbss7-lnzin76e2slizeol3w2qzplday.us-east-1.es.amazonaws.com"
os.environ["ES_INDEX"] = "cloudtrail"
os.environ["REPLICATION_TARGET_SECRETNAME"] = "/eq-LogMonitoring-Test/targetaccountcredentials"
os.environ["NOTIFICATION_TOPIC_ARN"] = "arn:aws:sns:us-east-1:376773251456:eq-LogMonitoring-Test-rFileSyncSNS-1HZMPRRG9AMPG"



sync_files.handler(s3testevent,context)


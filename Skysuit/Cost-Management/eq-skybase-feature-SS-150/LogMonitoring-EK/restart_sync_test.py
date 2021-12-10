import os
import json
from restart_sync import restart_sync



testevent = {"rrr": "ttt"}


class context:
    requestid=1111
    invoked_function_arn = "arn:aws:lambda:us-east-1:834800198471:function:ST-s3syncv9-rSyncFilesLambda-V0U93NH5PY1X"


Context = context()



os.environ["EVENTSOURCE_MAPPING_UUID"] = "3a180d62-9b01-4eb1-8d56-1ebf8fd0e2f3"
os.environ["DEAD_LETTER_QUEUE_URL"] = "https://sqs.us-east-1.amazonaws.com/834800198471/St-s3sync10-rDeadLetterSqsQueue-KASMATBWL2WB"
os.environ["MAIN_QUEUE_URL"] = "https://sqs.us-east-1.amazonaws.com/834800198471/St-s3sync10-rMainSqsQueue-NXR8Z92W67XW"
os.environ["NOTIFICATION_TOPIC_ARN"] = "arn:aws:sns:us-east-1:834800198471:St-s3sync10-rFileSyncSNS-Q62TPNAGFQVG"

ret = restart_sync.handler(testevent,context)
print(ret)


# restart_sync.move_messages("https://sqs.us-east-1.amazonaws.com/834800198471/St-s3sync10-rMainSqsQueue-NXR8Z92W67XW", "https://sqs.us-east-1.amazonaws.com/834800198471/St-s3sync10-rDeadLetterSqsQueue-KASMATBWL2WB")

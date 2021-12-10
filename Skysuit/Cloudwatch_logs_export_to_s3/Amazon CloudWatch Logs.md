# Amazon CloudWatch Logs

Amazon CloudWatch Logs to monitor, store, and access your log files from Amazon Elastic Compute Cloud (Amazon EC2) instances, AWS CloudTrail, Route 53, and other sources.

CloudWatch Logs enables you to centralize the logs from all of your systems, applications, and AWS services that you use, in a single, highly scalable service. You can then easily view them, search them for specific error codes or patterns, filter them based on specific fields, or archive them securely for future analysis.

**Log events**

A log event is a record of some activity recorded by the application or resource being monitored. The log event record that CloudWatch Logs understands contains two properties: the timestamp of when the event occurred, and the raw event message. Event messages must be UTF-8 encoded.

**Log streams**

A log stream is a sequence of log events that share the same source. More specifically, a log stream is generally intended to represent the sequence of events coming from the application instance or resource being monitored. For example, a log stream may be associated with an Apache access log on a specific host. When you no longer need a log stream, you can delete it using the [aws logs delete-log-stream](https://docs.aws.amazon.com/cli/latest/reference/logs/delete-log-stream.html) command.

**Log groups**

Log groups define groups of log streams that share the same retention, monitoring, and access control settings. Each log stream has to belong to one log group. For example, if you have a separate log stream for the Apache access logs from each host, you could group those log streams into a single log group called `MyWebsite.com/Apache/access_log`.

There is no limit on the number of log streams that can belong to one log group.

**Metric filters**

You can use metric filters to extract metric observations from ingested events and transform them to data points in a CloudWatch metric. Metric filters are assigned to log groups, and all of the filters assigned to a log group are applied to their log streams.

**Retention settings**

Retention settings can be used to specify how long log events are kept in CloudWatch Logs. Expired log events get deleted automatically. Just like metric filters, retention settings are also assigned to log groups, and the retention assigned to a log group is applied to their log streams.

**AWS Services Used In Solution**

- AWS CloudWatch - Logs to be exported.

- AWS S3 - to keep Logs Backup.

- AWS CloudFormation Template - to automate the solution.



**Solution Design**





![123](D:\Skysuit\Cloudwatch_logs_export_to_s3\123.png)





**Deployment**

- The Cloudwatch logs to be monitored should be in the lambda comma(,) separated.
  1-  The log group filter will match log group "as-is", i.e it is ASSUMED to be case sensitive,  So make sure the correct log group                          	  full names as it appears in the env variable. 

  ​		For example: "/aws/lambda/log-group-name". 

  ​		For multiple log groups:              "/aws/lambda/lg1,/aws/lambda/lg2,/aws/lambda/lg3

  2-  The S3 Bucket MUST be in the same region
  3-  The `retention_days` defaults to 90 days, Customize in `global_vars`
  4-  AWS CW Log exports doesn't effectively keep track of logs that are exported previously in a       native way. 
  5-  To avoid exporting the same data twice, this script uses a timeframe of 24 hour period.               This period is the 90th day in the past.

  6-  Run the script everyday to keep the log export everyday.
  ----------------------|<------LOG EXPORT PERIOD------>|----------------------------------------|
                  91stDay                        90thDay                                   Today
  7-  The default time for awaiting task completion is 5 Minutes(300 Seconds). Customize in `      global_vars`
  8-  FROM AWS Docs,Export task:One active (running or pending) export task at a time, per        account. This limit cannot be changed.
  -- Ref[1] -https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/cloudwatch_limits_cwl.html
  9-  Increase Lambde Timeout based on requirements.
  10- Lambda IAM - Role: CloudWatch Access List/Read & S3 Bucket - HEAD, List, Put.

  **Parameters in Template**

  | Parameter                 | Description                                                  | Allowed values     |
  | ------------------------- | ------------------------------------------------------------ | ------------------ |
  | pCloudwatchLogsBucketName | Name of the S3 Bucket Inwhich Logs are to be archived        | lower case         |
  | pRetentionDays            | The number of days older logs to be archived. Defaults to '90' | Number             |
  | pLogGroupName             | Name of cloudwatch logs to  export in S3 Bucket              | CommaDelimitedList |

  
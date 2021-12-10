

# Automate the life cycle of default CloudWatch log



This section covers an introductory note about CloudWatch and deployment steps.

### Amazon CloudWatch Logs

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

**Log Retention** – By default, logs are kept indefinitely and never expire. You can adjust the retention policy for each log group, keeping the indefinite retention, or choosing a retention period between 10 years and one day.



**AWS Services Used In Solution**

- AWS CloudWatch - Logs to be exported.

- AWS Lambda - to run the codes (the version of the python code developed is 3.7)

- AWS S3 - to keep Logs Backup.

- AWS CloudFormation Template - to automate the solution.

  

**Solution Design**





![Solution Diagram](https://user-images.githubusercontent.com/60149354/107239065-4dc7dc80-6a4a-11eb-8e9d-c81301fe66f1.png)



**Deployment**



1. The cloudformation template will create s3 bucket in the same region,put bucket policy, export the cloudwatch logs to s3 bucket through lambda function and cloudwatch rule to trigger lambda everday.

2. The log group filter will match log group by "retention period". 

3. AWS CW Log exports doesn't effectively keep track of logs that are exported previously in a native way. 

4. To avoid exporting the same data twice, this function uses a timeframe of 24 hour period. This period is the 1 day in the past.

5. Lambda function will run to keep the log export everyday.

6. The default time for awaiting task completion is 5 Minutes(300 Seconds). Customize in `global_vars`.

7. FROM AWS Docs,Export task: One active (running or pending) export task at a time, per account. This limit cannot be changed.

   https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/cloudwatch_limits_cwl.html

8. Increase Lambde Timeout based on requirements.

9. Lambda IAM - Role: CloudWatch Access List/Read & S3 Bucket - HEAD, List, Put.

10.You need to Trigger lambda munal first time, then it will trigger Automaticaly on daily basis.

**Parameters in Template**

| Parameter                 | Description                                           | Allowed values                                               |
| ------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| pCloudwatchLogsBucketName | Name of the S3 Bucket Inwhich Logs are to be archived | lower case                                                   |
| pTargetId                 | Name for the target ID to cloudwatch rule.            | Include alphanumeric characters, periods (.), hyphens (-), and underscores (_). |

Navigate into the path "Cloudwatch_logs_export_to_s3\CloudformationTemplate" and use cloudformation packaged command given below:

First package 

```
aws cloudformation package --template-file </path_to_template/template.yml> --s3-bucket bucket-name --output-template-file <packaged-template.yml>
```

Then Deploy

```
aws cloudformation deploy --template-file </path_to_template/template.yml> --stack-name <my-new-stack> --parameter-overrides <Key1=Value1 Key2=Value2> --tags <Key1=Value1 Key2=Value2> --capabilities CAPABILITY_IAM
```


AWS Bill Summary Report for each account
2021-03-04 v1.0

========================================
A. Package Contents
========================================
a. CloudFormationTemplates\NestedTemplate\bill-summary-report-nested.yml

b. CloudFormationTemplates\bill-contact-parameters.yml

c. CloudFormationTemplates\bill-summary-report.yml

d. Lambdas\bill-contact-parameters.zip

e. Lambdas\bill-summary-report.zip

f. readme.md (this file)

===============================================================
B. Verification of Email Addresses in AWS Simple Email Service
===============================================================
1. Log into the master account, open Simple Email Service (SES) and go to Email Addresses.

2. Click on "Verify a New Email Address".

3. Enter the Email Adress and click on "Verify This Email Address".

4. You will get an email from AWS to confirm the email address.

5. Check the email of organization master account is verfied or not in SES. If not, verify the master account id as well 
	e.g. skybase-master@enquizit.com

===============================================================
C. Creation of S3 Bucket and deployment of Bill Summary Report
===============================================================
1. Create a bucket in the region where this package will be deployed - e.g. bill-summary-bucket (referred to as <bucket> below).

2. Upload the file bill-contact-parameters.zip to <bucket/Lambdas> folder. 

3. Upload the file bill-summary-report.zip to <bucket/Lambdas> folder.

4. Upload the file bill-contact-parameters.yml to <bucket/CloudFormationTemplates> folder.

5. Upload the file bill-summary-report.yml to <bucket/CloudFormationTemplates> folder.

6. Make sure that the bucket can be accessed by the master account.

7. Log into the master account and go to the CloudFormation service.

8. Select "Create stack" and choose the option "With new resources (standard)".

9. Choose "Template is Ready" and "Upload Template".

10. Click "Choose file" and upload the file "bill-summary-report-nested.yml" under CloudFormationTemplates\NestedTemplate\ folder included in the package.  

11. Click "Next".

13. Enter a name for the stack.

14. Enter the parameters requested.  Each has an explanation. (For testing purpose, you can change the cron job to your local time. By Default the Cron
   is set to 9:00 AM  UTC every 3rd of the month)

12. Click "Next".

11. Click "Next".

12. Acknowledge that CFN will create IAM Resources and click "Create Stack".

Output: This template creates two nested stacks, two lambda functions, a CloudWatch event rule and a SNS topic.
		You can find the names/arns in the output section of the CloudFormation stack.

Note: You will get an email from AWS to subscribe the sns topic. Please do confirm the subscription.	

===========================
D. Testing
===========================
1. Go to the CloudWatch. Select the event rule which got created above.

2. Change the cron job timing to your local time so that the lambda gets triggered and generates the bill summary report for each account for the previous month.

3. At the scheduled time, a report is generated and sent to the email address mentioned as a parameter value. 

4. The report consists of Total Bill Due and Bill Amount by each service for the previous month for each account.

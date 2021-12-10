AWS Patch Manager Setup
2020-06-24
(c) Enquizit Inc.
v1.0

========================================
A. Package Contents
========================================
a. patch-manager-setup-MM.yml
b. readme.txt (this file)

=====================================================
B. Deploying the resources
=====================================================
1. It is best to set this up as a stackset.  This way any changes made to the CFT over time are automatically pushed to all accounts.  You manage the patch baselines and patch windows using the CFT.

2. To start, deploy the resources into a test account to make sure everything works to your satisfaction


=====================================================
C. Creating the Resources (single account stack)
=====================================================
1. Log in to your account.

2. Go to the CloudFormation services page.

3. Click on "Create stack" and select "With new resources (standard).

4. Select "Template is ready".

5. Select "Upload a template file".

6. Click on "Choose file" and select the file "patch-manager-setup-MM.yml" attached to this package.

7. Click Next.

8. On the next page, enter a stack name (e.g. patch-manager-stack).

9. Enter the following for each of the parameters for the full install (option (B)(1)(a) above):
	a. Organization
		i. Company name - Mathematica; this will be used to tag resources
	b. Maintenance Windows
		i. Maintenance window for production - Cron expression; pattern for cron expression is cron(ss mm hh ? * DAY *).
		ii. Maintenance window for non-production - Cron expression; pattern for cron expression is cron(ss mm hh ? * DAY *).
	c. Tags
		i. WindowsTags - Tags that will identify Windows instances
		ii. LinuxTags - Tags that will identify Linux instances
		iii. Tags to identify prod servers - Tags to identify production servers
		iv. Tags to identify non-prod servers - Tags to identify non-prod servers
NOTE: The total set of tags defined in the group (Windows Tags, Linux Tags) MUST be the same as the set of tags defined in the group (Prod Tags, Non-Prod Tags)

	d. Notification
		i. Notification email address - address where patch manager notifications will be sent
	e. Sample Fleet
		i. Create Fleet - Yes if you want to test with a sample set of instances
		ii. Latest Linux AMI - don't change this value
		iii. Latest Windows AMI - don't change this value
	
10. Click Next.

11. Click Next again.

12. Review the parameters and then click "Create stack".

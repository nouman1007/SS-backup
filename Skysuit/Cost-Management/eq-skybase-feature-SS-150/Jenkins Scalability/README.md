## Scalable Architecture Of Jenkins Architecture via AWS ECS

It is pretty common when starting with Jenkins to have a single server which runs the master and all builds, however, Jenkins architecture is fundamental “Master+Agent”. Jenkins scalability gives you lots of benefits:

- the ability to run many more build plans in parallel

- automatically replacing corrupted Jenkins instances

- automatically spinning up and removing slaves based on need, which saves costs

- distributing the load across different physical machines while keeping required resources available for each specific build plan

======================================== 

## Design for Scalability of jenkins on Demand.

Read more details about design at below link:
https://enquizit.atlassian.net/wiki/spaces/ON/pages/2078703805/Scalable+Architecture+for+Jenkins+Environment?atlOrigin=eyJpIjoiYzc4YTljZmVmYTMwNDNmNmEwMzMzZTM1NmYxNTIwZjkiLCJwIjoiYyJ9

## Package Contents:

Package contains :

1. network_configuration.yaml

    Creates tiered VPC with Public and Private subnets, sopanning an AWS Region. Also creates NAT gateway to handle outbound traffic.

2. jenkins-for-ecs-with-agents-autoconfigured.yaml

    Creates Highly available ECS Cluster deployed across two AZ in private subnet. 
    
    Also creates Application load balancer in front of internet to handle inbound traffic. 
    
    Centralized logging with AWS CloudWatch Logs.

    It has AWS EFS file system for storing jenkin's configuration and data.


3. README.md (this file)



## Prerequisite
1. Login to AWS Account(Master/Member) and select region where to upload **network_configuration.yaml** to S3 bucket. Upload manually or run following command.
   
        aws s3 cp <path of file> s3://<Bucket name> --profile <profile of account>
        
2. Copy the Url of key uploaded in step 1 and paste in line 31 of **jenkins-for-ecs-with-agents-autoconfigured.yaml** at field TemplateURL.

## Deployment steps.

1. Log into the same account where you have uploaded the **network_configuration.yaml** file in bucket.

2. Select CloudFormation in Services Search bar.

3. Select 'Create Stack'.

4. Select 'Template is Ready', 'Upload a template file' and then 'Choose file'. Select the file **jenkins-for-ecs-with-agents-autoconfigured.yaml** which is included with this package.

5. Click 'Next'.

6. Enter a name for the Stack e.g. Jenkins-master-slave-stack.

7. Enter the following parameters: 

    |Parameters|Description|Allowed Values|
    -----------|------------|---------------|
    |ClusterName|Specify name for cluster|jenkins-master-slave-cluster|
    |JenkinsJNLPPort|Port at which slave communicates with master|50000
    |JenkinsUsername|User name foR Jenkins to login|developer|
   
    ----------------------------------------------------------------------------------

8. Click 'Next'.

9. Check the box "I acknowledge that AWS CloudFormation might create IAM resources."

10. Click 'Submit'.

### Result:

Following resources will be created:

- Application load balancer with its security group and listener.

- Security group for master jenkins allowing in traffic from load balancer and to traffic to slave jenkins.

- Security group for slave agents for allowing traffic to master jenkins only via JNLP(Java Network lAUNCH Protocol) port.

- ECS Cluster 

- ECS task Definition that describes how containers should launch by specific Image, network details for port mapping, Volume etc.

- ECS Servics that runs the task on containers having same task defination. It also registers itself with the load balancer.

- EFS for file syatem and security group for it.

- Mount targets in different AZs for HA.

- Password in AWS Secret Manager to login in Jenkins.

|Resource|Description|
|--------------------------------------|------------------------------------- |
|VPCStack|Network components including public private subnets, route tables etc|
|LoadBalancer|Application load balancer in front of internet|
|LoadBalancerSecurityGroup|Security group for ALB handling inbound traffic and allowing outbound traffic to JenkinsSecurityGroup |
|LoadBalancerListener|ALB listener is listening traffic at port 8080 and forwarding it to JenkinsTargetGroup|
|ALBListener|Listening traffic at port 80 and redirectingit to port 8080 listener|
|JenkinsTargetGroup|Target group for load balancer|
|JenkinsSecurityGroup|Allowing inbound traffic at port 8080 from LoadBalancerSecurityGroup|
|JenkinsAgentSecurityGroup|Allowing inbound traffic at JNLP port(from parameter) from JenkinsSecurityGroup|
|ECS Cluster|ECS Cluster used to launch Docker containers on AWS|
|JenkinsExecutionRole|Role that grants the Amazon ECS container agent permission to make AWS API calls.|
|JenkinsRole|Grants containers in the task permission to call AWS APIs|
|JenkinsTaskDefinition|Describes the container and volume definitions of Amazon ECS task. You can specify which Docker images to use, the required resources, and other configurations related to launching the task definition through an Amazon ECS service or task.<br>**Custom Image**: tkgregory/jenkins-ecs-agents:latest is able to install all plugins needed to setup AWS ECS on jenkins via plugins and scripts.|
|JenkinsService|Defines long-running tasks of the same Task Definition. This can be one running container or multiple running containers all using the same Task Definition|
|CloudwatchLogsGroup|Log of ecs cluster|
|FileSystemResource|For storing jenkin's configurationand job data.|
|EFSSecurityGroup|Allowing inbound traffic to EFS from JenkinsSecurityGroup at port 2048|
|MountTargetResource1|Creates mount target for EFS in private subnet one|
|MountTargetResource2|Creates mount target for EFS in private subnet two|
|AccessPointResource|An access point is an application-specific view into an EFS that applies an operating system user and group, and a file system path,to any file system request made through the access point.|
|PrivateNamespace|Enable the Jenkins slave to communicate with the Jenkins master without going outside of our private AWS network.|
|DiscoveryService|enkins slave can communicate with the master|
|JenkinsMasterPasswordSecret|Creates a secret and stores it in Secrets Manager|

## Demo

1. Get the password from secret manager console or run following command.

        - aws secretsmanager get-secret-value --secret-id JenkinsMasterPasswordSecret --profile <profile name> --region <region name>

2. Get DNS Name of load balancer and browse it. It pops up the Jenkins Welcome page.

3. Provide JenkinsUserName provided at time of setup (Deployment Step #7) and Password retrived from step 1 (Demo).

4. Click on slave-test pipeline and build now.

5. Slave agent is started for jobs and task is created in ECS Console. As soon as job is done, agent will be removed and task is stopped now, hence saving the cost and fulfilling the scalability in jenkins slave.

---

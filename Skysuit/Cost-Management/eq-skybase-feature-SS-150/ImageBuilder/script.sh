#!/bin/bash
yum update -y
yum install zip unzip -y
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
sudo systemctl enable amazon-ssm-agent
sleep 120
export ami="centos"
export now=$(date +"%H-%M-%S")
export latest=${ami}-${now}
export IID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id) 
sleep 60                           
export AMI=$(aws ec2 create-image --instance-id $IID --name "$latest" --no-reboot --region <region selected> --output text)
sleep 480
export JSON_PAYLOAD='{"ami":"'"$AMI"'","instanceID":"'"$IID"'"}'
aws lambda invoke --function-name <name of function> --payload $JSON_PAYLOAD --cli-binary-format raw-in-base64-out --region <region selected> response.json
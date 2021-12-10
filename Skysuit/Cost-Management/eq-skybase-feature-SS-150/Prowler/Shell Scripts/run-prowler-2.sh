#!/bin/bash -e
source .awsvariables
echo "S3: $S3"
cd prowler/output
./scripts.sh
cd ..
aws s3 cp output/ "$S3/reports/" --recursive --include "*.json-asff"

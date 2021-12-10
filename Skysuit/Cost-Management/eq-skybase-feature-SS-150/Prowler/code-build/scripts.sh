#!/bin/bash -e
for FILE in *; do title=$(echo $FILE|awk -F '-'  {'print $3'})
sudo mkdir -p $title/ 
sudo cp -p prowler-output-$title* $title/ ;done

sudo rm -r prowler-output-*

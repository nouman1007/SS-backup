#   Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import boto3
import logging
import json
import cfnresponse

client = boto3.client('events')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def create_trust(accounts):
   for account in accounts:
        response = client.put_permission(
            Action= 'events:PutEvents',
            Principal= account,
            StatementId= 'limtr-{}'.format(account)
        )

def remove_trust(accounts):
    for account in accounts:
        response = client.remove_permission(
            StatementId= 'limtr-{}'.format(account))

def create(properties, old_properties,physical_id):
    account_ids = properties["ACCOUNT_IDS"]
    account_ids = account_ids.replace("\"","")
    account_list = account_ids.split(",")
    if account_list:
        logger.debug(account_list)
        create_trust(account_list)
    return cfnresponse.SUCCESS, physical_id


def update(properties, old_properties, physical_id):
    account_ids = properties["ACCOUNT_IDS"]
    account_ids = account_ids.replace("\"","")
    account_list = account_ids.split(",")
    old_account_ids = old_properties["ACCOUNT_IDS"]
    old_account_ids = old_account_ids.replace("\"","")
    old_account_list = old_account_ids.split(",")
    if account_list and old_account_list:
        logger.debug(old_account_list)
        remove_trust(old_account_list)
        logger.debug(account_list)
        create_trust(account_list)
    return cfnresponse.SUCCESS, physical_id


def delete(properties, old_properties, physical_id):
    account_ids = properties["ACCOUNT_IDS"]
    account_ids = account_ids.replace("\"","")
    account_list = account_ids.split(",")
    if account_list:
        remove_trust(account_list)
    return cfnresponse.SUCCESS, physical_id


def handler(event, context):
    logger.info('Received event: %s' % json.dumps(event))
    status = cfnresponse.FAILED
    new_physical_id = None
    try:
        properties = event.get('ResourceProperties')
        old_properties = event.get('OldResourceProperties')
        physical_id = event.get('PhysicalResourceId')
        status, new_physical_id = {'Create': create, 'Update': update, 'Delete':
                                    delete}.get(event['RequestType'], lambda x, y: (cfnresponse.FAILED,
                                                                                    None))(properties, old_properties, physical_id)
    except Exception as e:
        logger.error('Exception:%s' % e)
        status = cfnresponse.FAILED
    finally:
        cfnresponse.send(event, context, status, {}, new_physical_id)
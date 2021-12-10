import json
import gzip
import datetime
import boto3
import os
import hashlib
import hmac
import base64
import urllib.parse
import time
import tempfile
import urllib3
import re
import logging

logger = logging.getLogger()
loglevel = os.environ.get('loglevel', 'INFO')  # will set default level of 'INFO' if env variable is not set 
logger.setLevel(loglevel)


http = urllib3.PoolManager()

source_client = boto3.client('s3')

CLOUDTRAIL = "CloudTrailProcessing"
REGEX_CLOUDTRAIL = "^[^\/]*/AWSLogs/[^\/]*/CloudTrail/[^\n]+" # Todo:Move this to env var, make sure CF temp can handle it
     

class EnvVariables:
    """
    Environment variable to be used in functions as inheritance.  
    """
    def __init__(self):          
        self.EVENT_TRIGGER_PAUSE_THRESHOLD = int(os.environ.get("EVENT_TRIGGER_PAUSE_THRESHOLD","-1"))    # set this first
        self.NOTIFICATION_TOPIC_ARN = os.environ["NOTIFICATION_TOPIC_ARN"]
        self.HOST = os.environ.get('ES_HOST')
        self.REGION = os.environ.get('AWS_REGION', "us-east-1")  
        self.INDEXNAME =  os.environ.get('ES_INDEX', "cloudtrail")   # default set to cloudtrail
        self.ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
        self.SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN')

def handler(event, context):
    """
    Lambda handler function, recieve event and context as arguments 
    """
    try:

        if __debug__:  # setting logger to log in console when debugging
            print ('Debug ON')
            ch = logging.StreamHandler()
            logger.addHandler(ch)


        logger.info(f"Sync Event Details: {json.dumps(event)}")

        ENV_VARS = EnvVariables()       # setting all environment variables here so missing variable errors will happen at the beginning      

        records = event['Records']

        for record in records:
            process_record(record, ENV_VARS)
                    
    except Exception as e:        
        logger.error(f'Upload file to ES Error: {e}  ;  Event: {json.dumps(event)}')
        raise e

def getFileType(source_key_: str) -> str:
    """
    This function filter cloudtrail logs from source_key(full path of cloudtrail logs from s3 bucket)
    """    
    if re.search(REGEX_CLOUDTRAIL, source_key_):
        return CLOUDTRAIL
    else:
        return "ignore"


def process_record(_record, _envvars: EnvVariables):
    """
    Function used to get information from event comming from handler function. Filtring source_bucket name
    and path of log file, then push event Json to another function (feed_es).
    """    
    logger.info(f"SQS Record: {json.dumps(_record)}")

    msg_str = _record['body']
    msg = json.loads(msg_str)
    
    if ("Event" in msg.keys()) and (msg["Event"] == "s3:TestEvent"):
        #if s3 test event, ignore
        logger.warn("Ignoring s3 test event")
    else:
        
        source_bucket = msg['Records'][0]['s3']['bucket']['name']
        source_key = urllib.parse.unquote(msg['Records'][0]['s3']['object']['key'])
        
        logger.info(f"Source Bucket: {source_bucket} ; Source Key: {source_key}")

        
        if getFileType(source_key) == CLOUDTRAIL:

            obj_size = msg['Records'][0]['s3']['object']['size']
            
            if obj_size == 0:     # if cloudtrail log file is 0
                logger.info("Found cloudtrail log file size 0 Exiting..")
            else:
                feed_es(source_bucket, source_key, _envvars)
                response_msg = source_key + ' was successfully copied from ' + source_bucket + ' to ES'
        else:
            logger.info(f"ignoring {source_key} since it is not in the allowed list")


def sign(key, msg):
    """
    Function used in the aws signed url
    """    
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region_name, service_name):
    """
    Function used in the aws signed url
    """    
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing

def feed_es(_bucket : str, _key: str, _envvars: EnvVariables):
    """
    Function used to move cloud trail data(json record) from s3 to Elasticsearch
    """

    method = 'POST'
    service = 'es'
    content_type = 'application/json'


    logger.info("feeding cloudtrail data to ES")
    s3obj = tempfile.NamedTemporaryFile(mode='w+b',delete=False)

    # downloads file to above path
    source_client.download_fileobj(_bucket, _key, s3obj)

    s3obj.close()
    gzfile = gzip.open(s3obj.name, "r")

    # loads contents of the Records key into variable (our actual cloudtrail log entries!)
    response = json.loads(gzfile.readlines()[0])
    
    """ 
    Filtering CloudDigest logs from source bucket. Cloud trail logs have Record in responce so, restrictng cloudtrail disget event. 
    """
    if( "Records" not in response ):
        logger.warn("Not CloudTrail. Exiting.. {_key}")
        return

    eventcount = 1
    # loops over the events in the json
    for i in response["Records"]:
        # filtering out some  unneccassary events as an example.
        if ( i["eventName"] == "describeInstanceHealth" ):
            continue
        
        # apiVersion causes problems with the index mapping.
        # The -right- solution would be to solve it with a proper mapping.
        i.pop( 'apiVersion', None )

        # adds @timestamp field = time of the event
        i["@timestamp"] = i["eventTime"]

        # removes .aws.amazon.com from eventsources
        i["eventSource"] = i["eventSource"].split(".")[0]
        data = json.dumps(i).encode('utf-8')
        # print( "data:\n---\n{}\n---\n".format( data ))

        # defines correct index name based on eventTime,  an index for each day on ES
        event_date = i["eventTime"].split("T")[0]

        canonical_uri = f'/{_envvars.INDEXNAME}-{event_date}/_doc'
        # url endpoint for ES cluster
        url = 'https://' + _envvars.HOST + canonical_uri
        # print( "Event {} url : {}\n".format(eventcount, url))

        # aws signed url 
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d')
        canonical_querystring = ''
        canonical_headers = 'content-type:' + content_type + '\n' + \
                            'host:' + _envvars.HOST + '\n' + \
                            'x-amz-date:' + amz_date + '\n'
        signed_headers = 'content-type;host;x-amz-date'
        payload_hash = hashlib.sha256(data).hexdigest()
        canonical_request = method + '\n' + \
                            canonical_uri + '\n' + \
                            canonical_querystring + '\n' + \
                            canonical_headers + '\n' + \
                            signed_headers + '\n' + \
                            payload_hash
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = date_stamp + '/' + _envvars.REGION + '/' + service + '/' + 'aws4_request'
        string_to_sign = algorithm + '\n' + \
                         amz_date + '\n' + \
                         credential_scope + '\n' + \
                         hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        signing_key = get_signature_key(_envvars.SECRET_KEY, date_stamp, _envvars.REGION, service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        authorization_header = algorithm + ' ' + \
                               'Credential=' + _envvars.ACCESS_KEY + '/' + credential_scope + ', ' + \
                               'SignedHeaders=' + signed_headers + ', ' + \
                               'Signature=' + signature
        headers = {'Content-Type':content_type,
                   'X-Amz-Date':amz_date,
                   'Authorization':authorization_header, 'X-Amz-Security-Token': _envvars.SESSION_TOKEN}

        # sending json data to elasticsearch using urllib3
        req = http.request('POST', url, body=data, headers=headers)
        
        # print( "Attempt 0 status code: {}".format(req.status))
        # print( "response:\n---\n{}\n---\n".format( req.text ))

        retry_counter = 1

        """
        if data sending fail for some reason, this will retry 3 times.

        """
        # if status code is not successfull, and retry counter is less than 4 resend data again
        while (req.status != 201) and (retry_counter < 4):
        # print( "Got code {}. Retrying {} of 3".format( req.status_code, retry_counter) )

            # sending data to ES again
            req = http.request('POST', url, body=data, headers=headers)

            # print( "status code: {}".format(req.status))
            retry_counter += 1
        eventcount +=1

    s3obj.close()
    os.unlink(s3obj.name)
    print( "{} events in {}".format(eventcount, s3obj.name) )


def get_destination_bucket(source_bucket: str, bucketmapping_pattern: str) -> str:
    """expects the source_bucket to follow the pattern <accountnum>-middlepart eg: '12345678910-sb-cloudtrail'
        expects bucketmapping_pattern to contain '<sourcebucketnamewithoutaccountnumber>' eg: 252383483717-<sourcebucketnamewithoutaccountnumber>-pub
        replaces '<sourcebucketnamewithoutaccountnumber>' in bucketmapping_pattern with middlepart from source_bucket and returns
    """
    destination_bucket = ""
    
    if source_bucket.find("-") == -1:
        raise Exception(f"Invalid source bucket name '{source_bucket}''. Expected pattern <accountnum>-middlepart eg: '12345678910-sb-cloudtrail'")
    else:
        SourceBucket_withoutaccountnum = source_bucket.split('-', 1)[1]
    
    if bucketmapping_pattern.find("<sourcebucketnamewithoutaccountnumber>") == -1 :
        raise Exception(f"Invalid BUCKET_MAPPING_PATTERN env variable {bucketmapping_pattern}. Pattern must include '<sourcebucketnamewithoutaccountnumber>' eg: '123456789-<sourcebucketnamewithoutaccountnumber>-pub'.")
    else:
        destination_bucket = bucketmapping_pattern.replace("<sourcebucketnamewithoutaccountnumber>", SourceBucket_withoutaccountnum)
        
    return destination_bucket    
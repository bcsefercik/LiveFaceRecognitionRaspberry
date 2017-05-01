import boto
import boto.exception
import boto.sns
import pprint
import re
import json

def send_push(body, access_key_id, secret_access_key, device_id):
    region = [r for r in boto.sns.regions() if r.name==u'us-west-1'][0]

    sns = boto.sns.SNSConnection(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region=region,
    )   
    
    try:
        endpoint_response = sns.create_platform_endpoint(
            platform_application_arn='arn:aws:sns:us-west-1:899067923163:app/APNS_SANDBOX/HoosTRY',
            token=device_id,
        )   
        endpoint_arn = endpoint_response['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']
    except boto.exception.BotoServerError, err:
        # Yes, this is actually the official way:
        # http://stackoverflow.com/questions/22227262/aws-boto-sns-get-endpoint-arn-by-device-token
        result_re = re.compile(r'Endpoint(.*)already', re.IGNORECASE)
        result = result_re.search(err.message)
        if result:
            endpoint_arn = result.group(0).replace('Endpoint ','').replace(' already','')
        else:
            raise
            
    print "ARN:", endpoint_arn
    body = {'aps': {'alert': body, 'sound': 'default'}}
    body_json = json.dumps(body, ensure_ascii=False)

    message = {'default': 'The default message',
           'APNS_SANDBOX': body_json}

    MESSAGE_JSON = json.dumps(message, ensure_ascii=False)
    publish_result = sns.publish(
        target_arn=endpoint_arn,
        message=MESSAGE_JSON,
        message_structure='json',
    )
    print "PUBLISH"
    pprint.pprint(publish_result)